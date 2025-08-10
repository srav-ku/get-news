from typing import Dict, Any
from flask import Request

def validate_news_params(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize query parameters for news endpoint
    """
    # Get parameters with defaults
    keyword = args.get('keyword', 'technology')
    category = args.get('category')
    country = args.get('country')
    language = args.get('language', 'en')
    
    # Validate keyword
    if not keyword or not keyword.strip():
        keyword = 'technology'
    
    # Validate category (if provided)
    valid_categories = [
        'general', 'business', 'entertainment', 'health', 
        'science', 'sports', 'technology'
    ]
    if category and category.lower() not in valid_categories:
        raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
    
    # Validate country (if provided) - support comma-separated priority list
    valid_countries = [
        'us', 'in', 'uk', 'fr', 'de', 'ca', 'au', 'jp', 'kr', 'cn', 'br', 'mx', 'it', 'es'
    ]
    if country:
        # Handle comma-separated country priority list
        countries = [c.strip().lower() for c in country.split(',')]
        for c in countries:
            if c not in valid_countries:
                raise ValueError(f"Invalid country code '{c}'. Must be one of: {', '.join(valid_countries)}")
        country = ','.join(countries)  # Return normalized format
    
    # Validate language - expanded support
    valid_languages = ['en', 'hi', 'te', 'ta', 'bn', 'fr', 'es', 'de']
    if language not in valid_languages:
        raise ValueError(f"Invalid language. Must be one of: {', '.join(valid_languages)}")
    
    return {
        'keyword': keyword.strip(),
        'category': category.lower() if category else None,
        'country': country if country else None,  # Already normalized above
        'language': language.lower()
    }
