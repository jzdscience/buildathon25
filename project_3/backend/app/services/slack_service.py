import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.socket_mode.aiohttp import SocketModeClient as AsyncSocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from sqlalchemy.orm import Session
import logging
import json

from ..config import settings
from ..models.database import MonitoredChannel, Message, Reaction, get_db
from .sentiment_service import SentimentService

logger = logging.getLogger(__name__)


class SlackService:
    def __init__(self):
        self.client = AsyncWebClient(token=settings.slack_bot_token)
        self.socket_client = None
        self.sentiment_service = SentimentService()
        self.is_monitoring = False
        
    async def initialize_socket_mode(self):
        """Initialize socket mode client for real-time events"""
        if settings.slack_app_token:
            self.socket_client = AsyncSocketModeClient(
                app_token=settings.slack_app_token,
                web_client=self.client
            )
            self.socket_client.socket_mode_request_listeners.append(self._handle_socket_mode_events)
    
    async def start_monitoring(self):
        """Start monitoring Slack channels"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        logger.info("Starting Slack monitoring...")
        
        # Initialize socket mode if configured
        await self.initialize_socket_mode()
        
        # Start real-time monitoring if socket mode is available
        if self.socket_client:
            await self.socket_client.connect()
            logger.info("Socket mode connected for real-time monitoring")
        
        # Start periodic polling for historical data
        asyncio.create_task(self._periodic_channel_sync())
    
    async def stop_monitoring(self):
        """Stop monitoring Slack channels"""
        self.is_monitoring = False
        if self.socket_client:
            await self.socket_client.disconnect()
        logger.info("Slack monitoring stopped")
    
    async def _handle_socket_mode_events(self, client: AsyncSocketModeClient, req: SocketModeRequest):
        """Handle real-time Slack events"""
        try:
            if req.type == "events_api":
                event = req.payload["event"]
                
                if event["type"] == "message":
                    await self._process_message_event(event)
                elif event["type"] == "reaction_added":
                    await self._process_reaction_event(event, added=True)
                elif event["type"] == "reaction_removed":
                    await self._process_reaction_event(event, added=False)
            
            # Acknowledge the request
            await client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))
            
        except Exception as e:
            logger.error(f"Error handling socket mode event: {e}")
    
    async def _periodic_channel_sync(self):
        """Periodically sync messages from monitored channels"""
        while self.is_monitoring:
            try:
                await self.sync_all_channels()
                await asyncio.sleep(settings.sentiment_update_interval_minutes * 60)
            except Exception as e:
                logger.error(f"Error in periodic channel sync: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def sync_all_channels(self):
        """Sync messages from all monitored channels"""
        db = next(get_db())
        try:
            channels = db.query(MonitoredChannel).filter(MonitoredChannel.is_active == True).all()
            
            for channel in channels:
                await self.sync_channel_messages(channel.channel_id, db)
                
        finally:
            db.close()
    
    async def sync_channel_messages(self, channel_id: str, db: Session, days_back: int = 7):
        """Sync messages from a specific channel"""
        try:
            # Calculate oldest timestamp to fetch
            oldest = datetime.utcnow() - timedelta(days=days_back)
            oldest_ts = oldest.timestamp()
            
            # Get channel history
            response = await self.client.conversations_history(
                channel=channel_id,
                oldest=str(oldest_ts),
                limit=200
            )
            
            if response["ok"]:
                messages = response["messages"]
                
                for msg_data in messages:
                    await self._process_message_data(msg_data, channel_id, db)
                    
                # Handle pagination
                while response.get("has_more", False):
                    response = await self.client.conversations_history(
                        channel=channel_id,
                        oldest=str(oldest_ts),
                        cursor=response["response_metadata"]["next_cursor"],
                        limit=200
                    )
                    
                    if response["ok"]:
                        for msg_data in response["messages"]:
                            await self._process_message_data(msg_data, channel_id, db)
                    else:
                        break
                        
                db.commit()
                logger.info(f"Synced messages for channel {channel_id}")
                
            else:
                logger.error(f"Failed to fetch messages for channel {channel_id}: {response['error']}")
                
        except Exception as e:
            logger.error(f"Error syncing channel {channel_id}: {e}")
            db.rollback()
    
    async def _process_message_event(self, event: Dict[str, Any]):
        """Process real-time message event"""
        db = next(get_db())
        try:
            await self._process_message_data(event, event["channel"], db)
            db.commit()
        except Exception as e:
            logger.error(f"Error processing message event: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def _process_message_data(self, msg_data: Dict[str, Any], channel_id: str, db: Session):
        """Process a single message and store in database"""
        try:
            message_id = msg_data.get("ts")
            if not message_id:
                return
            
            # Check if message already exists
            existing = db.query(Message).filter(Message.message_id == message_id).first()
            if existing:
                return
            
            # Skip bot messages and system messages
            if msg_data.get("subtype") in ["bot_message", "channel_join", "channel_leave"]:
                return
            
            text = msg_data.get("text", "")
            user_id = msg_data.get("user", "")
            timestamp = datetime.fromtimestamp(float(message_id))
            
            # Analyze sentiment
            text_sentiment = self.sentiment_service.analyze_text_sentiment(text)
            emoji_sentiment = self.sentiment_service.analyze_emoji_sentiment(text)
            overall_sentiment = (text_sentiment + emoji_sentiment) / 2 if emoji_sentiment != 0 else text_sentiment
            
            # Check for thread
            has_thread = "thread_ts" in msg_data or "replies" in msg_data
            
            # Create message record
            message = Message(
                message_id=message_id,
                channel_id=channel_id,
                user_id=user_id,
                text=text,
                timestamp=timestamp,
                text_sentiment=text_sentiment,
                emoji_sentiment=emoji_sentiment,
                overall_sentiment=overall_sentiment,
                has_thread=has_thread,
                reaction_count=len(msg_data.get("reactions", []))
            )
            
            db.add(message)
            
            # Process reactions
            if "reactions" in msg_data:
                for reaction_data in msg_data["reactions"]:
                    emoji = reaction_data["name"]
                    count = reaction_data["count"]
                    emoji_score = self.sentiment_service.get_emoji_sentiment_score(emoji)
                    
                    reaction = Reaction(
                        message_id=message_id,
                        emoji=emoji,
                        count=count,
                        sentiment_score=emoji_score
                    )
                    db.add(reaction)
            
            # Process thread replies if present
            if has_thread and "thread_ts" in msg_data:
                await self._process_thread_replies(msg_data["thread_ts"], channel_id, db)
                
        except Exception as e:
            logger.error(f"Error processing message data: {e}")
    
    async def _process_thread_replies(self, thread_ts: str, channel_id: str, db: Session):
        """Process replies in a thread"""
        try:
            response = await self.client.conversations_replies(
                channel=channel_id,
                ts=thread_ts
            )
            
            if response["ok"]:
                messages = response["messages"]
                for msg_data in messages[1:]:  # Skip the parent message
                    await self._process_message_data(msg_data, channel_id, db)
                    
        except Exception as e:
            logger.error(f"Error processing thread replies: {e}")
    
    async def _process_reaction_event(self, event: Dict[str, Any], added: bool):
        """Process reaction added/removed event"""
        db = next(get_db())
        try:
            message_id = event["item"]["ts"]
            emoji = event["reaction"]
            
            # Find existing reaction
            reaction = db.query(Reaction).filter(
                Reaction.message_id == message_id,
                Reaction.emoji == emoji
            ).first()
            
            if added:
                if reaction:
                    reaction.count += 1
                else:
                    emoji_score = self.sentiment_service.get_emoji_sentiment_score(emoji)
                    reaction = Reaction(
                        message_id=message_id,
                        emoji=emoji,
                        count=1,
                        sentiment_score=emoji_score
                    )
                    db.add(reaction)
            else:
                if reaction:
                    reaction.count = max(0, reaction.count - 1)
                    if reaction.count == 0:
                        db.delete(reaction)
            
            # Update message reaction count
            message = db.query(Message).filter(Message.message_id == message_id).first()
            if message:
                total_reactions = db.query(Reaction).filter(Reaction.message_id == message_id).count()
                message.reaction_count = total_reactions
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error processing reaction event: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def add_channel(self, channel_id: str, db: Session) -> MonitoredChannel:
        """Add a new channel to monitor"""
        try:
            # Get channel info
            response = await self.client.conversations_info(channel=channel_id)
            
            if not response["ok"]:
                raise Exception(f"Failed to get channel info: {response['error']}")
            
            channel_info = response["channel"]
            channel_name = channel_info["name"]
            
            # Check if already exists
            existing = db.query(MonitoredChannel).filter(MonitoredChannel.channel_id == channel_id).first()
            if existing:
                existing.is_active = True
                existing.channel_name = channel_name
                existing.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(existing)
                return existing
            
            # Create new monitored channel
            channel = MonitoredChannel(
                channel_id=channel_id,
                channel_name=channel_name
            )
            db.add(channel)
            db.commit()
            db.refresh(channel)
            
            # Start syncing this channel
            await self.sync_channel_messages(channel_id, db)
            
            return channel
            
        except Exception as e:
            db.rollback()
            raise e
    
    async def remove_channel(self, channel_id: str, db: Session) -> bool:
        """Remove a channel from monitoring"""
        try:
            channel = db.query(MonitoredChannel).filter(MonitoredChannel.channel_id == channel_id).first()
            if channel:
                channel.is_active = False
                channel.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(channel)
                return True
            return False
            
        except Exception as e:
            db.rollback()
            raise e
    
    async def get_monitored_channels(self, db: Session) -> List[MonitoredChannel]:
        """Get list of monitored channels"""
        try:
            channels = db.query(MonitoredChannel).filter(MonitoredChannel.is_active == True).all()
            for channel in channels:
                db.refresh(channel)
            return channels
        except Exception as e:
            db.rollback()
            raise e
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Slack API connection"""
        try:
            response = await self.client.auth_test()
            return {
                "success": response["ok"],
                "user": response.get("user"),
                "team": response.get("team"),
                "url": response.get("url"),
                "error": response.get("error")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
