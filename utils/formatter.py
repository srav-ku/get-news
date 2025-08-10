import logging
from typing import List, Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def format_chat_response(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Format news articles for chat presentation with both raw data and formatted response
    """
    if not articles:
        return {
            "data": [],
            "formatted_response": "📰 **No news articles found** 📰\n\nTry searching with different keywords or check back later for fresh content!"
        }
    
    # Build formatted chat response
    formatted_lines = ["📰 **Latest News** 📰\n"]
    
    for i, article in enumerate(articles, 1):
        title = article.get('title', 'Untitled')
        summary = article.get('summary', article.get('content', 'No summary available'))
        sentiment = article.get('sentiment', {})
        source = article.get('source', 'Unknown Source')
        published_at = article.get('publishedAt', '')
        
        # Format sentiment
        sentiment_emoji = sentiment.get('emoji', '😐')
        sentiment_label = sentiment.get('label', 'neutral').title()
        
        # Format timestamp
        time_str = format_time_ago(published_at)
        
        # Build article section
        formatted_lines.extend([
            f"🔥 **{i}. {title}**\n",
            f"📝 {summary}\n",
            f"{sentiment_emoji} **Sentiment:** {sentiment_label}\n",
            f"📰 **Source:** {source}\n",
            f"🕒 **Published:** {time_str}\n",
            "---\n"
        ])
    
    # Remove last separator
    if formatted_lines and formatted_lines[-1] == "---\n":
        formatted_lines.pop()
    
    formatted_response = "\n".join(formatted_lines)
    
    # Add follow-up suggestions based on content
    follow_up_suggestions = generate_follow_up_suggestions(articles)
    
    if follow_up_suggestions:
        formatted_response += "\n\n💡 **More Topics You Might Like:**\n" + follow_up_suggestions
    
    return {
        "data": articles,
        "formatted_response": formatted_response,
        "total_articles": len(articles),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "follow_up_suggestions": follow_up_suggestions
    }

def format_time_ago(published_at: str) -> str:
    """
    Convert ISO datetime to human-readable time ago format
    """
    if not published_at:
        return "Unknown time"
    
    try:
        # Parse the datetime
        if 'T' in published_at:
            published_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        else:
            published_time = datetime.fromisoformat(published_at)
        
        # Ensure timezone awareness
        if published_time.tzinfo is None:
            published_time = published_time.replace(tzinfo=timezone.utc)
        
        # Calculate time difference
        now = datetime.now(timezone.utc)
        diff = now - published_time
        
        # Format human-readable time
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
            
    except Exception as e:
        logger.warning(f"Error parsing time {published_at}: {str(e)}")
        return "Unknown time"

def create_simple_sentiment(content: str) -> Dict[str, str]:
    """
    Simple rule-based sentiment analysis fallback
    """
    if not content:
        return {"label": "neutral", "emoji": "😐"}
    
    content_lower = content.lower()
    
    # Positive indicators
    positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 
                     'breakthrough', 'success', 'win', 'achievement', 'progress', 'growth',
                     'innovation', 'advance', 'improvement', 'positive', 'benefit']
    
    # Negative indicators  
    negative_words = ['bad', 'terrible', 'awful', 'crisis', 'problem', 'issue', 'concern',
                     'decline', 'drop', 'fall', 'crash', 'failure', 'loss', 'damage',
                     'threat', 'risk', 'danger', 'negative', 'controversy']
    
    positive_count = sum(1 for word in positive_words if word in content_lower)
    negative_count = sum(1 for word in negative_words if word in content_lower)
    
    if positive_count > negative_count:
        return {"label": "positive", "emoji": "😊"}
    elif negative_count > positive_count:
        return {"label": "negative", "emoji": "😠"}
    else:
        return {"label": "neutral", "emoji": "😐"}

def create_simple_summary(content: str, max_length: int = 80) -> str:
    """
    Simple text summarization fallback - returns first sentences up to max_length
    """
    if not content:
        return content
    
    if len(content) <= max_length:
        return content
    
    # Find sentence boundaries
    sentences = content.split('. ')
    summary = ""
    
    for sentence in sentences:
        if len(summary + sentence + '. ') <= max_length:
            summary += sentence + '. '
        else:
            break
    
    # If no complete sentences fit, truncate
    if not summary:
        summary = content[:max_length-3] + "..."
    
    return summary.strip()

def generate_follow_up_suggestions(articles: List[Dict[str, Any]]) -> str:
    """Generate smart follow-up topic suggestions based on article content"""
    if not articles:
        return ""
    
    # Analyze article content for smart suggestions
    all_content = " ".join([
        article.get('title', '') + " " + article.get('content', '')
        for article in articles
    ]).lower()
    
    suggestions = []
    
    # Indian cinema suggestions
    if any(term in all_content for term in ['bollywood', 'tollywood', 'kollywood', 'indian', 'hindi', 'telugu', 'tamil']):
        suggestions.extend([
            "🎬 [More Bollywood News](/news/topic/bollywood?language=hi&country=in)",
            "🎭 [Telugu Cinema Updates](/news/topic/tollywood?language=te&country=in)",
            "🎪 [Tamil Movies News](/news/topic/kollywood?language=ta&country=in)"
        ])
    
    # Technology suggestions
    if any(term in all_content for term in ['ai', 'artificial intelligence', 'machine learning', 'tech']):
        suggestions.extend([
            "🤖 [More AI News](/news/topic/artificial-intelligence?category=technology)",
            "💻 [Tech Innovations](/news/topic/technology-innovation?language=en)"
        ])
    
    # Sports suggestions  
    if any(term in all_content for term in ['cricket', 'football', 'sports', 'match', 'tournament']):
        suggestions.extend([
            "🏏 [Cricket Updates](/news/topic/cricket?country=in,uk,au)",
            "⚽ [Football News](/news/topic/football?country=us,uk,de)"
        ])
    
    # Entertainment suggestions
    if any(term in all_content for term in ['movie', 'film', 'actor', 'actress', 'celebrity']):
        suggestions.extend([
            "🌟 [Celebrity News](/news/topic/celebrity?category=entertainment)",
            "🎥 [Movie Reviews](/news/topic/movie-reviews?language=en)"
        ])
    
    # Return first 3 suggestions
    if suggestions:
        return "\n".join(suggestions[:3])
    
    # Default suggestions if no specific matches
    return "\n".join([
        "🔥 [Breaking News](/news/topic/breaking-news?language=en)",
        "🇮🇳 [India News](/news?country=in&language=hi)",
        "🌍 [World News](/news?country=us,uk,fr&language=en)"
    ])

def translate_to_language(text: str, target_language: str) -> str:
    """Simple translation fallback using basic word mapping"""
    if target_language == 'en' or not text:
        return text
    
    # Basic Telugu translations for common news terms
    if target_language == 'te':
        translations = {
            'news': 'వార్తలు',
            'latest': 'తాజా',
            'breaking': 'ఎక్కడిక',
            'technology': 'సాంకేతికత',
            'sports': 'క్రీడలు',
            'politics': 'రాజకీయాలు',
            'business': 'వ్యాపారం',
            'health': 'ఆరోగ్యం',
            'india': 'భారతదేశం',
            'cricket': 'క్రికెట్',
            'bollywood': 'బాలీవుడ్',
            'movie': 'సినిమా',
            'film': 'చిత్రం'
        }
        
        # Simple word replacement
        words = text.split()
        translated_words = []
        for word in words:
            clean_word = word.lower().strip('.,!?')
            if clean_word in translations:
                translated_words.append(translations[clean_word])
            else:
                translated_words.append(word)
        return ' '.join(translated_words)
    
    # Basic Hindi translations
    elif target_language == 'hi':
        translations = {
            'news': 'समाचार',
            'latest': 'नवीनतम',
            'breaking': 'ब्रेकिंग',
            'technology': 'प्रौद्योगिकी',
            'sports': 'खेल',
            'politics': 'राजनीति',
            'business': 'व्यापार',
            'health': 'स्वास्थ्य',
            'india': 'भारत',
            'cricket': 'क्रिकेट',
            'bollywood': 'बॉलीवुड',
            'movie': 'फिल्म'
        }
        
        words = text.split()
        translated_words = []
        for word in words:
            clean_word = word.lower().strip('.,!?')
            if clean_word in translations:
                translated_words.append(translations[clean_word])
            else:
                translated_words.append(word)
        return ' '.join(translated_words)
    
    return text  # Return original if no translation available