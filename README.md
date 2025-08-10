# AI News MCP Server

A Flask REST API server that fetches real-time news and processes it with AI for summarization, sentiment analysis, and multi-language translation.

## Features

- **Real-time News Fetching**: Uses both NewsAPI and GNews API for comprehensive news coverage
- **AI Summarization**: Summarizes articles using Hugging Face transformers
- **Sentiment Analysis**: Analyzes sentiment with emoji indicators (😊 positive, 😐 neutral, 😠 negative)
- **Multi-language Support**: Translates summaries to English, Hindi, Telugu, French, and Spanish
- **Latest News**: Returns top 5 latest articles sorted by publish date

## API Endpoints

### GET /news
Fetch and process news articles with AI analysis.

**Query Parameters:**
- `keyword` (optional): Topic search (default: "technology")
- `category` (optional): News category (general, business, entertainment, health, science, sports, technology)
- `country` (optional): Country code (us, in, fr, de, gb, ca, au, jp, kr, cn, br, mx, it, es)
- `language` (optional): Language for summary (en, hi, te, fr, es) - default: "en"

**Example:**
```bash
curl "http://localhost:5000/news?keyword=AI&category=technology&language=en"
```

**Response Format:**
```json
{
  "data": [
    {
      "title": "Latest AI Breakthrough in Healthcare",
      "content": "Full article content...",
      "summary": "AI summary of the article...",
      "sentiment": {
        "label": "positive",
        "emoji": "😊"
      },
      "source": "TechNews",
      "publishedAt": "2025-08-10T05:00:00Z",
      "language": "en"
    }
  ],
  "formatted_response": "📰 **Latest News** 📰\n\n🔥 **1. Latest AI Breakthrough...**\n📝 AI summary...\n😊 **Sentiment:** Positive\n...",
  "total_articles": 5,
  "timestamp": "2025-08-10T05:26:00+00:00"
}
