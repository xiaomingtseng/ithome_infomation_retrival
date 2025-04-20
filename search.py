from text_analyzer import TextAnalyzer
from tf_idf import TFIDFAnalyzer
from ckip_transformers.nlp import CkipWordSegmenter
from database import Database  

# 停用詞定義: 高頻詞、無意義詞、常用詞
# 高頻詞用TextAnalyzer的_remove_stopwords()方法過濾

class Search:
    def __init__(self, text: str, stopwords: list = None):
        self.text = text
        self.stopwords = stopwords if stopwords else []
        self.text_analyzer = TextAnalyzer(text, stopwords)
        self.tfidf_analyzer = TFIDFAnalyzer(stop_words=stopwords)

    def analyze_text(self):
        # 進行文本分析
        word_freq = self.text_analyzer.word_frequency()
        top_keywords = self.text_analyzer.top_keywords()
        unique_words = self.text_analyzer.unique_words()
        
        # 計算 TF-IDF
        tfidf_scores = self.tfidf_analyzer.compute_tfidf([{'content': self.text}])
        
        return {
            'word_frequency': word_freq,
            'top_keywords': top_keywords,
            'unique_words': unique_words,
            'tfidf_scores': tfidf_scores
        }

if __name__ == "__main__":
    # init database
    db_instance = Database()
    news_collection = db_instance.get_collection('news')

    # 停用詞列表
    text_analyzer = TextAnalyzer()
    stopwords = text_analyzer.stopwords