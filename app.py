import os
import logging
from flask import Flask, jsonify, request
from services.news_service import NewsService
from utils.validators import validate_news_params
from utils.formatter import format_chat_response

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Initialize services
news_service = NewsService()

# Try to import AI service, fallback to simple processing if unavailable
try:
    from services.ai_service import AIService
    ai_service = AIService()
    AI_AVAILABLE = True
    logger.info("AI services initialized successfully")
except ImportError as e:
    logger.warning(f"AI services not available: {str(e)}. Using simple fallback processing.")
    ai_service = None
    AI_AVAILABLE = False

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        "service": "AI News MCP Server",
        "version": "2.0.0",
        "status": "running",
        "description": "Production-ready Flask REST API for real-time news with AI processing",
        "endpoints": {
            "/health": "Health check endpoint",
            "/news": "Fetch processed news articles with AI analysis",
            "/news/topic/{topic}": "Get more news on a specific topic",
            "/news/languages": "Get supported languages",
            "/news/countries": "Get supported countries",
            "/getnews": "Puch AI compatible endpoint (case insensitive)",
            "/nlp": "Natural language processing for commands"
        },
        "example_usage": {
            "indian_movies": "/news?keyword=indian+movies&country=in&language=hi",
            "bollywood_news": "/news?keyword=bollywood&category=entertainment&country=in",
            "multilingual_tech": "/news?keyword=technology&language=te&country=in",
            "priority_country": "/news?keyword=cricket&country=in,us,uk",
            "follow_up_topic": "/news/topic/indian-movies?language=hi&country=in",
            "puch_ai_getnews": "/getnews?keyword=technology&lang=te",
            "puch_ai_latest": "/getNews (defaults to latest news)",
            "natural_language": "POST /nlp {\"text\": \"give me latest technology news in telugu\"}"
        },
        "features": {
            "indian_movies_support": "Dedicated support for Indian cinema news",
            "multi_language": "Support for en, hi, te, ta, bn, fr, es, de",
            "country_priority": "Set multiple countries in priority order",
            "topic_follow_up": "Ask for more news on searched topics",
            "sentiment_analysis": "Analyzes sentiment with emoji indicators",
            "summarization": "Intelligent text summarization",
            "chat_formatting": "Returns both structured data and chat-ready responses"
        },
        "supported_languages": {
            "en": "English", "hi": "Hindi", "te": "Telugu", "ta": "Tamil", 
            "bn": "Bengali", "fr": "French", "es": "Spanish", "de": "German"
        },
        "supported_countries": {
            "in": "India", "us": "United States", "uk": "United Kingdom", 
            "ca": "Canada", "au": "Australia", "fr": "France", "de": "Germany", "jp": "Japan"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "AI News MCP Server is running",
        "service": "AI News MCP Server"
    })

@app.route('/news', methods=['GET'])
def get_news():
    """
    Get processed news articles with AI analysis
    
    Query Parameters:
    - keyword: topic search (default: "technology")
    - category: news category (technology, sports, health, etc.)
    - country: country code (us, in, fr, etc.)
    - language: language for summary (en, hi, te, fr, es)
    """
    try:
        # Validate and extract query parameters
        params = validate_news_params(request.args)
        logger.info(f"Fetching news with params: {params}")
        
        # Fetch news articles
        articles = news_service.fetch_news(
            keyword=params['keyword'],
            category=params.get('category'),
            country=params.get('country'),
            language=params.get('language', 'en')
        )
        
        if not articles:
            return jsonify([])
        
        # Process articles with AI or fallback processing
        processed_articles = []
        for article in articles:
            try:
                content = article.get('content', '')
                target_language = params.get('language', 'en')
                
                if AI_AVAILABLE and ai_service:
                    # Use AI processing
                    summary = ai_service.summarize_text(content)
                    if target_language != 'en':
                        summary = ai_service.translate_text(summary, target_language)
                    sentiment = ai_service.analyze_sentiment(content)
                else:
                    # Use fallback processing
                    from utils.formatter import create_simple_summary, create_simple_sentiment
                    summary = create_simple_summary(content)
                    sentiment = create_simple_sentiment(content)
                
                # Build response
                processed_article = {
                    "title": article.get('title', ''),
                    "content": content,
                    "summary": summary,
                    "sentiment": sentiment,
                    "source": article.get('source', ''),
                    "publishedAt": article.get('publishedAt', ''),
                    "language": target_language
                }
                
                processed_articles.append(processed_article)
                
            except Exception as e:
                logger.error(f"Error processing article: {str(e)}")
                # Continue with other articles if one fails
                continue
        
        # Format response for chat
        response_data = format_chat_response(processed_articles)
        return jsonify(response_data)
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error occurred"}), 500

@app.route('/news/topic/<topic>', methods=['GET'])
def get_more_news_on_topic(topic):
    """Get more news articles on a specific topic (follow-up queries)"""
    try:
        # Convert topic to keyword format
        keyword = topic.replace('-', ' ').replace('_', ' ')
        
        # Get parameters with topic as keyword
        params = validate_news_params(request.args)
        params['keyword'] = keyword
        
        logger.info(f"Fetching more news for topic '{topic}' with params: {params}")
        
        # Fetch news articles
        articles = news_service.fetch_news(
            keyword=params['keyword'],
            category=params.get('category'),
            country=params.get('country'),
            language=params.get('language', 'en'),
            page_size=10  # Get more articles for follow-up
        )
        
        if not articles:
            return jsonify({
                "message": f"No more news found for topic: {topic}",
                "topic": topic,
                "articles": []
            })
        
        # Process articles
        processed_articles = []
        for article in articles:
            try:
                content = article.get('content', '')
                target_language = params.get('language', 'en')
                
                if AI_AVAILABLE and ai_service:
                    summary = ai_service.summarize_text(content)
                    if target_language != 'en':
                        summary = ai_service.translate_text(summary, target_language)
                    sentiment = ai_service.analyze_sentiment(content)
                else:
                    from utils.formatter import create_simple_summary, create_simple_sentiment
                    summary = create_simple_summary(content)
                    sentiment = create_simple_sentiment(content)
                
                processed_article = {
                    "title": article.get('title', ''),
                    "content": content,
                    "summary": summary,
                    "sentiment": sentiment,
                    "source": article.get('source', ''),
                    "publishedAt": article.get('publishedAt', ''),
                    "language": target_language
                }
                
                processed_articles.append(processed_article)
                
            except Exception as e:
                logger.error(f"Error processing article: {str(e)}")
                continue
        
        response_data = format_chat_response(processed_articles)
        response_data["topic"] = topic
        response_data["follow_up_query"] = True
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error getting more news for topic '{topic}': {str(e)}")
        return jsonify({"error": f"Failed to fetch more news for topic: {topic}"}), 500

@app.route('/news/languages', methods=['GET'])
def get_supported_languages():
    """Get list of supported languages"""
    return jsonify({
        "languages": {
            "en": "English",
            "hi": "Hindi", 
            "te": "Telugu",
            "ta": "Tamil",
            "bn": "Bengali",
            "fr": "French",
            "es": "Spanish",
            "de": "German"
        },
        "message": "Use the language code as 'language' parameter in news requests"
    })

@app.route('/news/countries', methods=['GET'])
def get_supported_countries():
    """Get list of supported countries"""
    return jsonify({
        "countries": {
            "in": "India",
            "us": "United States",
            "uk": "United Kingdom",
            "ca": "Canada",
            "au": "Australia",
            "fr": "France",
            "de": "Germany",
            "jp": "Japan"
        },
        "usage": {
            "single_country": "country=in",
            "priority_order": "country=in,us,uk (will try India first, then US, then UK)",
            "message": "Use country codes as 'country' parameter in news requests"
        }
    })

# Puch AI Compatible Endpoints
@app.route('/getnews', methods=['GET', 'POST'])
@app.route('/getNews', methods=['GET', 'POST'])
@app.route('/GetNews', methods=['GET', 'POST'])
def puch_ai_get_news():
    """Puch AI compatible endpoint - case insensitive getNews command"""
    try:
        # Handle both GET and POST requests
        if request.method == 'POST':
            data = request.get_json() or {}
            keyword = data.get('keyword') or data.get('topic')
            country = data.get('country')
            language = data.get('language') or data.get('lang')
            category = data.get('category')
        else:
            # GET request - use query parameters
            keyword = request.args.get('keyword') or request.args.get('topic')
            country = request.args.get('country')
            language = request.args.get('language') or request.args.get('lang')
            category = request.args.get('category')
        
        # Default to latest news if no keyword provided
        if not keyword:
            keyword = "latest"
            
        # Validate parameters
        params = {
            'keyword': keyword,
            'category': category,
            'country': country,
            'language': language or 'en'
        }
        
        validated_params = validate_news_params(params)
        logger.info(f"Puch AI request - Fetching news with params: {validated_params}")
        
        # Fetch and process news
        articles = news_service.fetch_news(
            keyword=validated_params['keyword'],
            category=validated_params.get('category'),
            country=validated_params.get('country'),
            language=validated_params.get('language', 'en'),
            page_size=5
        )
        
        if not articles:
            return jsonify({
                "status": "success",
                "message": "No news found for the specified criteria",
                "articles": [],
                "command": "getNews"
            })
        
        # Process articles with enhanced summarization
        processed_articles = []
        for article in articles:
            try:
                content = article.get('content', '')
                target_language = validated_params.get('language', 'en')
                
                # Create concise summary (max 80 words)
                if AI_AVAILABLE and ai_service:
                    summary = ai_service.summarize_text(content, max_length=80)
                    if target_language != 'en':
                        summary = ai_service.translate_text(summary, target_language)
                    sentiment = ai_service.analyze_sentiment(content)
                else:
                    from utils.formatter import create_simple_summary, create_simple_sentiment, translate_to_language
                    summary = create_simple_summary(content, max_length=80)
                    if target_language != 'en':
                        summary = translate_to_language(summary, target_language)
                    sentiment = create_simple_sentiment(content)
                
                processed_article = {
                    "title": article.get('title', ''),
                    "summary": summary,  # Only summary, no full content
                    "sentiment": sentiment,
                    "source": article.get('source', ''),
                    "publishedAt": article.get('publishedAt', ''),
                    "language": target_language
                }
                
                processed_articles.append(processed_article)
                
            except Exception as e:
                logger.error(f"Error processing article: {str(e)}")
                continue
        
        return jsonify({
            "status": "success",
            "message": f"Found {len(processed_articles)} news articles",
            "articles": processed_articles,
            "command": "getNews",
            "params": validated_params
        })
        
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "command": "getNews"
        }), 400
    except Exception as e:
        logger.error(f"Puch AI getNews error: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": "Failed to fetch news",
            "command": "getNews"
        }), 500

@app.route('/nlp', methods=['POST'])
def natural_language_processor():
    """Process natural language requests for Puch AI"""
    try:
        data = request.get_json() or {}
        text = data.get('text', '').lower()
        
        if not text:
            return jsonify({
                "status": "error",
                "message": "No text provided for processing"
            }), 400
        
        # Extract intent and parameters from natural language
        intent_result = extract_news_intent(text)
        
        if intent_result['intent'] == 'get_news':
            # Use extracted parameters to fetch news
            params = intent_result['params']
            
            articles = news_service.fetch_news(
                keyword=params.get('keyword', 'latest'),
                category=params.get('category'),
                country=params.get('country'),
                language=params.get('language', 'en'),
                page_size=5
            )
            
            # Process articles (summary only)
            processed_articles = []
            for article in articles:
                try:
                    content = article.get('content', '')
                    target_language = params.get('language', 'en')
                    
                    if AI_AVAILABLE and ai_service:
                        summary = ai_service.summarize_text(content, max_length=80)
                        if target_language != 'en':
                            summary = ai_service.translate_text(summary, target_language)
                        sentiment = ai_service.analyze_sentiment(content)
                    else:
                        from utils.formatter import create_simple_summary, create_simple_sentiment, translate_to_language
                        summary = create_simple_summary(content, max_length=80)
                        if target_language != 'en':
                            summary = translate_to_language(summary, target_language)
                        sentiment = create_simple_sentiment(content)
                    
                    processed_articles.append({
                        "title": article.get('title', ''),
                        "summary": summary,
                        "sentiment": sentiment,
                        "source": article.get('source', ''),
                        "publishedAt": article.get('publishedAt', ''),
                        "language": target_language
                    })
                except Exception as e:
                    logger.error(f"Error processing article: {str(e)}")
                    continue
            
            return jsonify({
                "status": "success",
                "intent": "get_news",
                "message": f"Found {len(processed_articles)} news articles",
                "articles": processed_articles,
                "extracted_params": params
            })
        
        else:
            return jsonify({
                "status": "error",
                "message": "Could not understand the request. Try 'get me latest news' or 'show technology news'"
            }), 400
            
    except Exception as e:
        logger.error(f"NLP processing error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to process natural language request"
        }), 500

def extract_news_intent(text: str) -> dict:
    """Extract intent and parameters from natural language text"""
    text = text.lower().strip()
    
    # News intent keywords
    news_keywords = ['news', 'latest', 'update', 'headlines', 'breaking', 'show', 'get', 'tell', 'give']
    
    if any(keyword in text for keyword in news_keywords):
        params = {}
        
        # Extract topic/keyword
        topics = {
            'technology': ['tech', 'technology', 'artificial intelligence', 'ai', 'software', 'computer'],
            'sports': ['sports', 'cricket', 'football', 'soccer', 'tennis', 'basketball'],
            'bollywood': ['bollywood', 'hindi movies', 'mumbai films'],
            'politics': ['politics', 'election', 'government', 'minister'],
            'health': ['health', 'medical', 'covid', 'vaccine', 'hospital'],
            'business': ['business', 'economy', 'stock', 'market', 'company']
        }
        
        for topic, keywords in topics.items():
            if any(keyword in text for keyword in keywords):
                params['keyword'] = topic
                break
        
        # Extract language
        languages = {
            'hindi': 'hi', 'telugu': 'te', 'tamil': 'ta', 'bengali': 'bn',
            'french': 'fr', 'spanish': 'es', 'german': 'de'
        }
        
        for lang_name, lang_code in languages.items():
            if lang_name in text:
                params['language'] = lang_code
                break
        
        # Extract country
        countries = {
            'india': 'in', 'indian': 'in', 'america': 'us', 'usa': 'us', 
            'britain': 'uk', 'uk': 'uk', 'france': 'fr', 'germany': 'de'
        }
        
        for country_name, country_code in countries.items():
            if country_name in text:
                params['country'] = country_code
                break
        
        return {'intent': 'get_news', 'params': params}
    
    return {'intent': 'unknown', 'params': {}}

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
