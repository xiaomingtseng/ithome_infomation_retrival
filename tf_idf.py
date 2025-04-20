import string
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from ckip_transformers.nlp import CkipWordSegmenter
import math
from text_analyzer import TextAnalyzer  # 引入 TextAnalyzer

class TFIDFAnalyzer:
    def __init__(self, text_analyzer=None, model="bert-base"):
        # 初始化 CKIP Transformers 分詞器
        self.ws_driver = CkipWordSegmenter(model=model)
        self.text_analyzer = text_analyzer if text_analyzer else TextAnalyzer()

    def preprocess(self, content):
        """
        使用 TextAnalyzer 過濾停用詞，並忽略標點符號（包括中文全形標點）
        """
        # 定義中文全形標點符號
        chinese_punctuation = "，。、；：「」『』（）《》〈〉【】——……！￥？"

        # 使用 CKIP 分詞
        words = self.ws_driver([content])[0]
        
        # 過濾標點符號（包括英文和中文標點）
        words = [word for word in words if word not in string.punctuation and word not in chinese_punctuation]

        # 使用 TextAnalyzer 過濾停用詞
        chinese_tokens = self.text_analyzer.collect_stopwords_by_pos(''.join([char for char in content if '\u4e00' <= char <= '\u9fff']))
        english_tokens = self.text_analyzer.collect_english_stopwords(''.join([char for char in content if char.isascii()]))
        
        # 過濾後的詞彙
        filtered_words = [word for word in words if word not in chinese_tokens and word not in english_tokens]
        return filtered_words

    def compute_tfidf(self, articles):
        tf_per_doc = []  # 每篇文章的詞頻
        df_counter = Counter()  # 文件頻率
        total_documents = len(articles)

        # 計算 TF 和 DF
        for article in articles:
            content = article.get('content', '')
            if content:
                filtered_words = self.preprocess(content)
                tf = Counter(filtered_words)
                tf_per_doc.append(tf)
                df_counter.update(set(filtered_words))

        # 計算 TF-IDF
        tfidf_scores = defaultdict(float)
        for doc_tf in tf_per_doc:
            for term, tf in doc_tf.items():
                idf = math.log(total_documents / (1 + df_counter[term]))  # 加 1 防止分母為 0
                tfidf_scores[term] += tf * idf

        # 排序 TF-IDF 分數
        sorted_tfidf = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_tfidf

# 使用範例
if __name__ == "__main__":
    # 初始化資料庫
    from database import Database
    db_instance = Database()
    news_collection = db_instance.get_collection('news')

    # 初始化 TextAnalyzer
    text_analyzer = TextAnalyzer(allowed_pos={
        "chinese": ["Na", "Nb", "Nc", "Nd", "Ncd", "VA"],  # 中文允許的詞性
        "english": {"NN", "NNS", "NNP", "NNPS", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "JJ", "JJR", "JJS"}  # 英文允許的詞性
    })

    # 定義分析的時間範圍（例如過去 7 天）
    days_to_analyze = 7
    start_date = datetime.now() - timedelta(days=days_to_analyze)

    # 從資料庫中提取最近 7 天的文章
    articles = list(news_collection.find({'published_time': {'$gte': start_date.strftime('%Y-%m-%d %H:%M:%S')}}))

    # 初始化 TF-IDF 分析器
    analyzer = TFIDFAnalyzer(text_analyzer=text_analyzer)

    # 計算 TF-IDF
    sorted_tfidf = analyzer.compute_tfidf(articles)

    # 找出出現頻率最高的 10 個關鍵字
    top_keywords = sorted_tfidf[:10]

    # 輸出結果
    print("近期熱門關鍵字（基於 TF-IDF）：")
    for keyword, score in top_keywords:
        print(f"{keyword}: {score:.4f}")