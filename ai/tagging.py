from keybert import KeyBERT
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import logging

class AutoTagger:
    def __init__(self):
        try:
            self.kw_model = KeyBERT()
            self.use_keybert = True
        except Exception as e:
            logging.warning(f"KeyBERT failed to load: {e}. Using TF-IDF fallback.")
            self.use_keybert = False
            self.vectorizer = TfidfVectorizer(max_features=100, stop_words=None)
        
        # Predefined topic keywords for Japanese context
        self.topic_keywords = {
            '学校': ['学校', '授業', '先生', '友達', '勉強', '宿題', '試験', 'テスト', '部活'],
            '仕事': ['仕事', '会社', '上司', '同僚', '残業', 'プロジェクト', '会議', '給料'],
            '恋愛': ['恋人', '彼氏', '彼女', 'デート', '好き', '愛', '恋', '結婚'],
            '家族': ['家族', '両親', '母', '父', '兄弟', '姉妹', '子供', '祖父母'],
            '健康': ['病気', '体調', '医者', '薬', '運動', 'ダイエット', '疲れ'],
            '趣味': ['映画', '音楽', 'ゲーム', '読書', '旅行', 'スポーツ', '料理'],
            '友人': ['友達', '友人', '仲間', '親友', '同級生']
        }
    
    def extract_tags(self, text, max_tags=5):
        """
        Extract relevant tags from text
        """
        tags = []
        
        # First, check for predefined topic keywords
        topic_tags = self._extract_topic_tags(text)
        tags.extend(topic_tags)
        
        # Then use KeyBERT or TF-IDF for additional keywords
        if self.use_keybert:
            keyword_tags = self._extract_with_keybert(text, max_tags - len(tags))
        else:
            keyword_tags = self._extract_with_tfidf(text, max_tags - len(tags))
        
        tags.extend(keyword_tags)
        
        # Remove duplicates and limit to max_tags
        unique_tags = list(dict.fromkeys(tags))[:max_tags]
        return unique_tags
    
    def _extract_topic_tags(self, text):
        """Extract tags based on predefined topic keywords"""
        found_topics = []
        text_lower = text.lower()
        
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_topics.append(topic)
        
        return found_topics
    
    def _extract_with_keybert(self, text, max_keywords):
        """Extract keywords using KeyBERT"""
        try:
            if max_keywords <= 0:
                return []
            
            keywords = self.kw_model.extract_keywords(
                text, 
                keyphrase_ngram_range=(1, 2), 
                stop_words=None,
                top_k=max_keywords
            )
            return [kw[0] for kw in keywords]
        except Exception as e:
            logging.error(f"KeyBERT extraction failed: {e}")
            return []
    
    def _extract_with_tfidf(self, text, max_keywords):
        """Fallback keyword extraction using TF-IDF"""
        try:
            if max_keywords <= 0:
                return []
            
            # Simple keyword extraction based on word frequency
            words = re.findall(r'\b\w+\b', text.lower())
            word_freq = {}
            for word in words:
                if len(word) > 2:  # Skip short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top keywords by frequency
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in top_words[:max_keywords]]
        except Exception as e:
            logging.error(f"TF-IDF extraction failed: {e}")
            return []

# Global instance
auto_tagger = AutoTagger()