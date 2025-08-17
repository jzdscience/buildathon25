import React from 'react';
import { MessageSquare, TrendingUp, Hash } from 'lucide-react';
import { ChannelData } from '../types';
import { Badge, SentimentMeter } from './common';

interface ChannelOverviewProps {
  channels: ChannelData[];
}

const ChannelOverview: React.FC<ChannelOverviewProps> = ({ channels }) => {
  const getSentimentBadgeVariant = (category: string) => {
    switch (category) {
      case 'very_positive': return 'success';
      case 'positive': return 'success';
      case 'neutral': return 'default';
      case 'negative': return 'warning';
      case 'very_negative': return 'danger';
      default: return 'default';
    }
  };

  const formatChannelName = (name: string) => {
    return name.startsWith('#') ? name : `#${name}`;
  };

  if (!channels || channels.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-gray-500">
        <div className="text-center">
          <Hash className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <div className="text-lg font-medium">No channels configured</div>
          <div className="text-sm">Add Slack channels to start monitoring team sentiment</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {channels.map((channel, index) => (
        <div 
          key={channel.channel_id}
          className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center">
              <div className="flex items-center justify-center w-8 h-8 bg-gray-100 rounded-full mr-3">
                <Hash className="w-4 h-4 text-gray-600" />
              </div>
              <div>
                <h4 className="text-sm font-semibold text-gray-900">
                  {formatChannelName(channel.channel_name)}
                </h4>
                <p className="text-xs text-gray-500">
                  {channel.channel_id.substring(0, 8)}...
                </p>
              </div>
            </div>
            
            <Badge variant={getSentimentBadgeVariant(channel.sentiment_category) as any}>
              {channel.sentiment_category.replace('_', ' ').toUpperCase()}
            </Badge>
          </div>

          <div className="grid grid-cols-3 gap-4">
            {/* Sentiment */}
            <div className="text-center">
              <SentimentMeter 
                value={channel.avg_sentiment} 
                size="sm" 
                showLabel={false}
              />
              <div className="mt-2">
                <div className="text-xs font-medium text-gray-900">Sentiment</div>
                <div className="text-xs text-gray-500">
                  {(channel.avg_sentiment * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="text-center">
              <div className="flex items-center justify-center w-10 h-10 bg-blue-100 rounded-full mx-auto mb-2">
                <MessageSquare className="w-5 h-5 text-blue-600" />
              </div>
              <div className="text-sm font-bold text-gray-900">{channel.total_messages}</div>
              <div className="text-xs text-gray-500">Messages</div>
            </div>

            {/* Engagement */}
            <div className="text-center">
              <div className="flex items-center justify-center w-10 h-10 bg-purple-100 rounded-full mx-auto mb-2">
                <TrendingUp className="w-5 h-5 text-purple-600" />
              </div>
              <div className="text-sm font-bold text-gray-900">
                {(channel.avg_engagement * 100).toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500">Engagement</div>
            </div>
          </div>

          {/* Progress bar for engagement */}
          <div className="mt-3">
            <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
              <span>Engagement Rate</span>
              <span>{(channel.avg_engagement * 100).toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${
                  channel.avg_engagement > 0.7 ? 'bg-green-500' :
                  channel.avg_engagement > 0.4 ? 'bg-yellow-500' :
                  'bg-red-500'
                }`}
                style={{ width: `${Math.max(5, channel.avg_engagement * 100)}%` }}
              />
            </div>
          </div>
        </div>
      ))}

      {/* Summary */}
      {channels.length > 1 && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h5 className="text-sm font-semibold text-gray-900 mb-2">Channel Summary</h5>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-gray-900">{channels.length}</div>
              <div className="text-xs text-gray-500">Channels</div>
            </div>
            <div>
              <div className="text-lg font-bold text-gray-900">
                {channels.reduce((sum, ch) => sum + ch.total_messages, 0)}
              </div>
              <div className="text-xs text-gray-500">Total Messages</div>
            </div>
            <div>
              <div className="text-lg font-bold text-gray-900">
                {((channels.reduce((sum, ch) => sum + ch.avg_sentiment, 0) / channels.length) * 100).toFixed(0)}%
              </div>
              <div className="text-xs text-gray-500">Avg Sentiment</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChannelOverview;

