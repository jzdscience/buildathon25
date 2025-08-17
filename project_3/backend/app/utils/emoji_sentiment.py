"""Emoji sentiment mapping for Slack reactions and messages"""

# Comprehensive emoji sentiment scores (-1 to 1)
EMOJI_SENTIMENT_MAP = {
    # Positive emotions (0.5 to 1.0)
    "😀": 0.8, "😃": 0.9, "😄": 0.9, "😁": 0.85, "😆": 0.9,
    "😅": 0.7, "😂": 0.9, "🤣": 0.95, "😊": 0.85, "😇": 0.9,
    "🙂": 0.6, "🙃": 0.5, "😉": 0.7, "😌": 0.7, "😍": 0.95,
    "🥰": 0.9, "😘": 0.85, "😗": 0.7, "😙": 0.7, "😚": 0.75,
    "😋": 0.7, "😛": 0.6, "😜": 0.65, "🤪": 0.6, "😝": 0.6,
    "🤗": 0.85, "🤩": 0.95, "🥳": 0.95, "😏": 0.5, "😎": 0.8,
    "🤓": 0.6, "🧐": 0.4, "👍": 0.8, "👏": 0.85, "🙌": 0.9,
    "🎉": 0.95, "🎊": 0.9, "🎈": 0.8, "✨": 0.85, "💪": 0.8,
    "🔥": 0.85, "💯": 0.9, "✅": 0.8, "💚": 0.85, "💙": 0.85,
    "💜": 0.85, "❤️": 0.9, "🧡": 0.85, "💛": 0.85, "🤍": 0.8,
    "👌": 0.75, "✌️": 0.7, "🤘": 0.7, "🤟": 0.85, "☺️": 0.8,
    "🌟": 0.85, "⭐": 0.8, "🌈": 0.9, "☀️": 0.8, "🏆": 0.95,
    "🥇": 0.95, "🚀": 0.9, "party_parrot": 0.9, "tada": 0.9,
    
    # Neutral emotions (-0.3 to 0.3)
    "😐": 0.0, "😑": -0.1, "😶": 0.0, "🤔": 0.1, "🤨": 0.0,
    "😮": 0.1, "😯": 0.1, "😲": 0.2, "😳": 0.1, "🥺": 0.2,
    "👀": 0.1, "👂": 0.0, "👃": 0.0, "👄": 0.0, "👅": 0.0,
    "🤷": 0.0, "🤦": -0.2, "🙄": -0.3, "😴": -0.1, "💤": -0.1,
    "📝": 0.1, "📊": 0.1, "📈": 0.3, "📉": -0.3, "🔍": 0.1,
    "💡": 0.3, "⚡": 0.2, "☕": 0.2, "🍕": 0.3, "🍔": 0.3,
    
    # Negative emotions (-1.0 to -0.3)
    "😒": -0.5, "😞": -0.6, "😔": -0.6, "😟": -0.5, "😕": -0.4,
    "🙁": -0.5, "☹️": -0.6, "😣": -0.7, "😖": -0.7, "😫": -0.8,
    "😩": -0.7, "🥺": -0.3, "😢": -0.7, "😭": -0.8, "😤": -0.6,
    "😠": -0.7, "😡": -0.85, "🤬": -0.9, "😈": -0.6, "👿": -0.8,
    "💀": -0.7, "☠️": -0.8, "💩": -0.6, "😰": -0.6, "😥": -0.6,
    "😓": -0.5, "🤯": -0.5, "😱": -0.7, "😨": -0.6, "😰": -0.6,
    "😥": -0.6, "🤢": -0.7, "🤮": -0.8, "🤧": -0.4, "😷": -0.5,
    "🤒": -0.6, "🤕": -0.6, "👎": -0.7, "💔": -0.8, "🖤": -0.5,
    "⛔": -0.6, "🚫": -0.6, "❌": -0.7, "⚠️": -0.4, "🔴": -0.5,
    "😿": -0.7, "🙀": -0.6, "💢": -0.7, "💥": -0.5, "🌧️": -0.4,
    "⛈️": -0.5, "🌩️": -0.5, "red_circle": -0.5, "x": -0.7,
    
    # Work-related emojis
    "📅": 0.1, "⏰": -0.1, "⏱️": -0.1, "⏳": -0.2, "💼": 0.0,
    "💻": 0.1, "⌨️": 0.1, "🖥️": 0.1, "📧": 0.0, "📬": 0.1,
    "📭": -0.1, "📮": 0.1, "✉️": 0.0, "📄": 0.0, "📃": 0.0,
    "📑": 0.0, "📋": 0.1, "📌": 0.1, "📍": 0.1, "🔒": 0.2,
    "🔓": -0.1, "🔑": 0.3, "🎯": 0.5, "📢": 0.2, "🔔": 0.1,
}

# Common Slack custom emoji mappings
CUSTOM_EMOJI_SENTIMENT = {
    "thumbsup": 0.8,
    "thumbsdown": -0.7,
    "clap": 0.85,
    "wave": 0.6,
    "eyes": 0.1,
    "thinking_face": 0.1,
    "sob": -0.8,
    "joy": 0.9,
    "heart": 0.9,
    "broken_heart": -0.8,
    "100": 0.9,
    "fire": 0.85,
    "rocket": 0.9,
    "boom": -0.3,
    "zzz": -0.1,
    "coffee": 0.2,
    "beer": 0.4,
    "pizza": 0.3,
    "cake": 0.5,
    "party": 0.9,
    "confetti": 0.9,
    "trophy": 0.95,
    "checkmark": 0.8,
    "heavy_check_mark": 0.8,
    "cross": -0.7,
    "warning": -0.4,
    "sos": -0.8,
    "rage": -0.9,
    "triumph": -0.7,
    "weary": -0.7,
    "tired_face": -0.6,
    "fearful": -0.7,
    "scream": -0.8,
    "disappointed": -0.6,
    "pensive": -0.5,
    "confused": -0.3,
    "slightly_smiling_face": 0.5,
    "neutral_face": 0.0,
    "expressionless": -0.1,
    "hugging_face": 0.85,
    "star-struck": 0.95,
    "zany_face": 0.6,
    "shushing_face": -0.1,
    "symbols_on_mouth": -0.8,
    "hand_over_mouth": 0.3,
    "nauseated_face": -0.7,
    "vomiting_face": -0.8,
    "sneezing_face": -0.3,
    "hot_face": -0.4,
    "cold_face": -0.4,
    "woozy_face": -0.5,
    "dizzy_face": -0.5,
    "exploding_head": -0.5,
    "cowboy": 0.6,
    "partying_face": 0.95,
    "disguised_face": 0.3,
    "sunglasses": 0.8,
    "nerd": 0.6,
    "monocle": 0.4,
    "concerned": -0.5,
    "slightly_sad": -0.4,
    "sad": -0.6,
    "confounded": -0.7,
    "white_frowning": -0.6,
    "persevere": -0.7,
    "sweat": -0.5,
    "astonished": 0.2,
    "flushed": 0.1,
    "pleading_face": -0.3,
    "frowning": -0.5,
    "anguished": -0.7,
    "cold_sweat": -0.6,
    "cry": -0.7,
    "drooling_face": 0.3,
    "yawning_face": -0.1,
    "smiling_face_with_tear": 0.4,
}


def get_emoji_sentiment(emoji: str) -> float:
    """
    Get sentiment score for an emoji
    
    Args:
        emoji: The emoji character or name
        
    Returns:
        Sentiment score between -1 and 1, or 0 if unknown
    """
    # Check direct emoji
    if emoji in EMOJI_SENTIMENT_MAP:
        return EMOJI_SENTIMENT_MAP[emoji]
    
    # Check custom emoji names (remove colons if present)
    emoji_name = emoji.strip(':').lower()
    if emoji_name in CUSTOM_EMOJI_SENTIMENT:
        return CUSTOM_EMOJI_SENTIMENT[emoji_name]
    
    # Check if it's in the standard map by name
    for em, score in EMOJI_SENTIMENT_MAP.items():
        if emoji_name == em:
            return score
    
    # Default to neutral if unknown
    return 0.0


def calculate_emoji_sentiment_from_text(text: str) -> float:
    """
    Calculate overall emoji sentiment from text containing emojis
    
    Args:
        text: Text potentially containing emojis
        
    Returns:
        Average sentiment score of all emojis found, or 0 if none
    """
    import re
    import emoji
    
    # Extract all emojis from text
    emojis = emoji.emoji_list(text)
    
    # Also extract Slack-style :emoji: patterns
    slack_emojis = re.findall(r':([a-z0-9_]+):', text)
    
    if not emojis and not slack_emojis:
        return 0.0
    
    scores = []
    
    # Get scores for Unicode emojis
    for emoji_dict in emojis:
        score = get_emoji_sentiment(emoji_dict['emoji'])
        if score != 0:
            scores.append(score)
    
    # Get scores for Slack emojis
    for slack_emoji in slack_emojis:
        score = get_emoji_sentiment(slack_emoji)
        if score != 0:
            scores.append(score)
    
    if not scores:
        return 0.0
    
    return sum(scores) / len(scores)


def get_emoji_category(sentiment_score: float) -> str:
    """
    Categorize emoji sentiment
    
    Args:
        sentiment_score: Sentiment score between -1 and 1
        
    Returns:
        Category string: 'positive', 'neutral', or 'negative'
    """
    if sentiment_score > 0.1:
        return 'positive'
    elif sentiment_score < -0.1:
        return 'negative'
    else:
        return 'neutral'

