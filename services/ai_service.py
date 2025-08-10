import logging
from transformers import pipeline
from typing import Dict
import torch

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        """Initialize AI pipelines"""
        self.device = 0 if torch.cuda.is_available() else -1
        
        try:
            # Initialize summarization pipeline
            self.summarizer = pipeline(
                "summarization",
                model="sshleifer/distilbart-cnn-12-6",
                device=self.device
            )
            logger.info("Summarization pipeline initialized")
            
            # Initialize sentiment analysis pipeline
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=self.device
            )
            logger.info("Sentiment analysis pipeline initialized")
            
            # Initialize translation pipelines
            self.translators = {}
            self._init_translators()
            
        except Exception as e:
            logger.error(f"Error initializing AI models: {str(e)}")
            raise
    
    def _init_translators(self):
        """Initialize translation pipelines for supported languages"""
        translation_models = {
            'hi': 'Helsinki-NLP/opus-mt-en-hi',  # Hindi
            'te': 'Helsinki-NLP/opus-mt-en-hi',  # Telugu (using Hindi model as fallback)
            'fr': 'Helsinki-NLP/opus-mt-en-fr',  # French
            'es': 'Helsinki-NLP/opus-mt-en-es',  # Spanish
        }
        
        for lang, model in translation_models.items():
            try:
                self.translators[lang] = pipeline(
                    "translation",
                    model=model,
                    device=self.device
                )
                logger.info(f"Translation pipeline for {lang} initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize translation for {lang}: {str(e)}")
    
    def summarize_text(self, text: str, max_length: int = 150, min_length: int = 30) -> str:
        """
        Summarize text using the summarization pipeline
        """
        if not text or len(text.strip()) < 50:
            return text
        
        try:
            # Limit input length for performance (512 tokens)
            input_text = text[:2048]  # Approximate token limit
            
            summary = self.summarizer(
                input_text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
            
            return summary[0]['summary_text']
            
        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            # Return truncated original text as fallback
            return text[:200] + "..." if len(text) > 200 else text
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of text and return label with emoji
        """
        if not text:
            return {
                "label": "neutral",
                "emoji": "😐"
            }
        
        try:
            # Limit input length for performance
            input_text = text[:512]
            
            result = self.sentiment_analyzer(input_text)
            sentiment_label = result[0]['label'].lower()
            
            # Map sentiment labels to our format
            sentiment_mapping = {
                'positive': {'label': 'positive', 'emoji': '😊'},
                'negative': {'label': 'negative', 'emoji': '😠'},
                'neutral': {'label': 'neutral', 'emoji': '😐'},
                # Handle different model outputs
                'label_0': {'label': 'negative', 'emoji': '😠'},
                'label_1': {'label': 'neutral', 'emoji': '😐'},
                'label_2': {'label': 'positive', 'emoji': '😊'},
            }
            
            return sentiment_mapping.get(sentiment_label, {
                "label": "neutral",
                "emoji": "😐"
            })
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return {
                "label": "neutral",
                "emoji": "😐"
            }
    
    def translate_text(self, text: str, target_language: str) -> str:
        """
        Translate text to target language
        """
        if not text or target_language == 'en':
            return text
        
        if target_language not in self.translators:
            logger.warning(f"Translation not available for language: {target_language}")
            return text
        
        try:
            translator = self.translators[target_language]
            result = translator(text)
            return result[0]['translation_text']
            
        except Exception as e:
            logger.error(f"Translation failed for {target_language}: {str(e)}")
            return text
