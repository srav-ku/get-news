# AI News MCP Server

## Overview

AI News MCP Server is a production-ready Flask REST API that fetches real-time news articles and processes them with AI capabilities for seamless integration with Puch AI chatbot systems. The server aggregates news from multiple sources (NewsAPI and GNews), then applies intelligent fallback processing with sentiment analysis and summarization to provide enriched news content. The system returns the top 5 most recent articles with both structured data and chat-ready formatted responses, including sentiment scores with emoji indicators and support for multiple languages.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework Architecture
- **Flask REST API**: Simple, lightweight web framework chosen for its simplicity and rapid development capabilities
- **Single application structure**: Monolithic design with clear separation of concerns through service layers
- **Route-based endpoints**: RESTful design with `/health` for monitoring and `/news` for core functionality

### Service Layer Architecture
- **NewsService**: Handles external news API integration and data aggregation
- **AIService**: Manages all AI/ML operations including summarization, sentiment analysis, and translation
- **Validator utilities**: Input validation and parameter normalization separated into utility functions
- **Dual news source strategy**: Combines NewsAPI and GNews for comprehensive coverage and redundancy

### AI/ML Pipeline Architecture
- **Hugging Face Transformers**: Chosen for its extensive model ecosystem and ease of use
- **Pipeline-based processing**: Uses HF's pipeline abstraction for simplified model loading and inference
- **GPU acceleration support**: Automatically detects and uses CUDA when available, falls back to CPU
- **Multi-model approach**: 
  - Summarization: `sshleifer/distilbart-cnn-12-6` for news-specific summarization
  - Sentiment: `cardiffnlp/twitter-roberta-base-sentiment-latest` for social media-trained sentiment analysis
  - Translation: Helsinki-NLP opus models for language-specific translation

### Data Processing Architecture
- **Real-time processing**: No persistent storage, processes news articles on-demand
- **Aggregation and sorting**: Combines multiple news sources and sorts by publication date
- **Content limitation**: Implements text truncation for AI model input constraints
- **Error resilience**: Graceful degradation when individual news sources or AI models fail

### Error Handling and Validation
- **Parameter validation**: Strict validation for country codes, categories, and language codes
- **Graceful degradation**: System continues operating even if one news source fails
- **Comprehensive logging**: Debug-level logging throughout the application for monitoring
- **Timeout management**: Configurable timeouts for external API calls

## External Dependencies

### News APIs
- **NewsAPI**: Primary news aggregation service with comprehensive global coverage
- **GNews API**: Secondary news source for additional coverage and redundancy
- **API Keys**: Requires valid API keys for both services (configured via environment variables)

### AI/ML Models (Hugging Face)
- **sshleifer/distilbart-cnn-12-6**: Pre-trained summarization model optimized for news content
- **cardiffnlp/twitter-roberta-base-sentiment-latest**: Social media-trained sentiment analysis model
- **Helsinki-NLP/opus-mt-en-***: Language-specific translation models for multi-language support

### Python Libraries
- **Flask**: Web framework for REST API implementation
- **transformers**: Hugging Face library for AI model integration
- **torch**: PyTorch backend for model inference and GPU acceleration
- **requests**: HTTP client for external API communication

### Runtime Dependencies
- **CUDA (optional)**: GPU acceleration for AI model inference
- **Internet connectivity**: Required for fetching news and downloading AI models on first run
- **Environment variables**: Configuration for API keys and session secrets