import os
import logging
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.newsapi_key = os.getenv("NEWS_API_KEY", "d4c92e160722416ba2e1782022053c86")
        self.gnews_key = os.getenv("GNEWS_API_KEY", "14070ffb7f65ac62046967f94b155818")
        
        self.newsapi_url = "https://newsapi.org/v2/everything"
        self.gnews_url = "https://gnews.io/api/v4/search"
        
        # Timeout for API requests
        self.timeout = 10
    
    def fetch_news(self, keyword: str = "technology", category: Optional[str] = None, 
                   country: Optional[str] = None, language: str = "en", page_size: int = 5) -> List[Dict]:
        """
        Fetch news from both NewsAPI and GNews with country priority support
        """
        all_articles = []
        countries_list = []
        
        # Handle country priority (comma-separated list)
        if country:
            countries_list = [c.strip() for c in country.split(',')]
            logger.info(f"Using country priority order: {countries_list}")
        
        # Enhance keyword for Indian movies/bollywood content
        enhanced_keyword = self._enhance_keyword_for_indian_content(keyword)
        
        # Fetch from NewsAPI
        try:
            newsapi_articles = self._fetch_from_newsapi(enhanced_keyword, language)
            all_articles.extend(newsapi_articles)
            logger.info(f"Fetched {len(newsapi_articles)} articles from NewsAPI")
        except Exception as e:
            logger.error(f"NewsAPI fetch failed: {str(e)}")
        
        # Fetch from GNews with country priority
        for i, country_code in enumerate(countries_list or [None]):
            try:
                gnews_articles = self._fetch_from_gnews(enhanced_keyword, category, country_code, language)
                # Tag articles with priority for sorting
                for article in gnews_articles:
                    article['country_priority'] = i
                all_articles.extend(gnews_articles)
                logger.info(f"Fetched {len(gnews_articles)} articles from GNews (country: {country_code})")
            except Exception as e:
                logger.error(f"GNews fetch failed for country {country_code}: {str(e)}")
        
        # If no specific countries, fetch general GNews articles
        if not countries_list:
            try:
                gnews_articles = self._fetch_from_gnews(enhanced_keyword, category, None, language)
                all_articles.extend(gnews_articles)
                logger.info(f"Fetched {len(gnews_articles)} articles from GNews")
            except Exception as e:
                logger.error(f"GNews fetch failed: {str(e)}")
        
        if not all_articles:
            logger.warning("No articles fetched from any source")
            return []
        
        # Sort by country priority first, then by publish date
        sorted_articles = sorted(
            all_articles, 
            key=lambda x: (
                x.get('country_priority', 999),  # Country priority first
                -self._parse_date(x.get('publishedAt', '')).timestamp()  # Then by date desc
            )
        )
        
        return sorted_articles[:page_size]
    
    def _fetch_from_newsapi(self, keyword: str, language: str) -> List[Dict]:
        """Fetch articles from NewsAPI"""
        params = {
            'q': keyword,
            'language': language,
            'sortBy': 'publishedAt',
            'pageSize': 10,
            'apiKey': self.newsapi_key
        }
        
        url = f"{self.newsapi_url}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=self.timeout) as response:
            data = json.loads(response.read().decode())
        articles = []
        
        for article in data.get('articles', []):
            if article.get('title') and article.get('description'):
                articles.append({
                    'title': article['title'],
                    'content': article.get('description', ''),
                    'source': article.get('source', {}).get('name', 'NewsAPI'),
                    'publishedAt': article.get('publishedAt', ''),
                    'url': article.get('url', '')
                })
        
        return articles
    
    def _fetch_from_gnews(self, keyword: str, category: Optional[str], 
                          country: Optional[str], language: str) -> List[Dict]:
        """Fetch articles from GNews"""
        params = {
            'q': keyword,
            'lang': language,
            'max': 10,
            'sortby': 'publishdate',
            'token': self.gnews_key
        }
        
        if category:
            params['category'] = category
        if country:
            params['country'] = country
        
        url = f"{self.gnews_url}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=self.timeout) as response:
            data = json.loads(response.read().decode())
        articles = []
        
        for article in data.get('articles', []):
            if article.get('title') and article.get('description'):
                articles.append({
                    'title': article['title'],
                    'content': article.get('description', ''),
                    'source': article.get('source', {}).get('name', 'GNews'),
                    'publishedAt': article.get('publishedAt', ''),
                    'url': article.get('url', '')
                })
        
        return articles
    
    def _enhance_keyword_for_indian_content(self, keyword: str) -> str:
        """Enhance keywords for better Indian content search"""
        keyword_lower = keyword.lower()
        
        # Indian movies/cinema keywords
        indian_movie_terms = {
            'indian movies': 'indian movies bollywood tollywood kollywood',
            'bollywood': 'bollywood hindi cinema mumbai films',
            'tollywood': 'tollywood telugu cinema hyderabad films',
            'kollywood': 'kollywood tamil cinema chennai films',
            'movies': f'{keyword} bollywood hindi telugu tamil',
            'cinema': f'{keyword} indian cinema bollywood'
        }
        
        # Check for Indian movie-related keywords
        for term, enhanced in indian_movie_terms.items():
            if term in keyword_lower:
                logger.info(f"Enhanced keyword '{keyword}' to '{enhanced}' for better Indian content")
                return enhanced
        
        # Add Indian context for generic entertainment terms
        if any(word in keyword_lower for word in ['entertainment', 'celebrity', 'actor', 'actress']):
            enhanced = f"{keyword} india bollywood"
            logger.info(f"Added Indian context to '{keyword}' -> '{enhanced}'")
            return enhanced
            
        return keyword
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object for sorting"""
        if not date_str:
            return datetime.min.replace(tzinfo=timezone.utc)
        
        try:
            # Try ISO format first
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                return datetime.fromisoformat(date_str)
        except:
            try:
                # Try other common formats
                return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except:
                return datetime.min.replace(tzinfo=timezone.utc)
