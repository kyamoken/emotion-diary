from transformers import pipeline
from textblob import TextBlob
import logging

class SentimentAnalyzer:
    def __init__(self):
        try:
            # Try to use BERT-based multilingual sentiment analysis
            self.classifier = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment",
                return_all_scores=True
            )
            self.use_bert = True
        except Exception as e:
            logging.warning(f"BERT model failed to load: {e}. Falling back to TextBlob.")
            self.use_bert = False
    
    def analyze_sentiment(self, text):
        """
        Analyze sentiment of text and return Positive/Negative/Neutral
        """
        if self.use_bert:
            return self._analyze_with_bert(text)
        else:
            return self._analyze_with_textblob(text)
    
    def _analyze_with_bert(self, text):
        try:
            results = self.classifier(text)
            # Get the highest scoring sentiment
            best_result = max(results[0], key=lambda x: x['score'])
            
            # Map BERT labels to our format
            label_mapping = {
                'POSITIVE': 'Positive',
                'NEGATIVE': 'Negative',
                '1 star': 'Negative',
                '2 stars': 'Negative', 
                '3 stars': 'Neutral',
                '4 stars': 'Positive',
                '5 stars': 'Positive'
            }
            
            return label_mapping.get(best_result['label'], 'Neutral')
        except Exception as e:
            logging.error(f"BERT analysis failed: {e}")
            return self._analyze_with_textblob(text)
    
    def _analyze_with_textblob(self, text):
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            return 'Positive'
        elif polarity < -0.1:
            return 'Negative'
        else:
            return 'Neutral'

# Global instance
sentiment_analyzer = SentimentAnalyzer()