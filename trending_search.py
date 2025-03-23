from datetime import datetime, timedelta
from collections import Counter, defaultdict
from database import Database
from ckip_transformers.nlp import CkipWordSegmenter
import math

# 初始化 CKIP Transformers 分詞器
ws_driver = CkipWordSegmenter(model="bert-base")

# 初始化資料庫
db_instance = Database()
news_collection = db_instance.get_collection('news')  # 使用 'news' 集合

# 定義停用詞表
stop_words = {"的", "是", "在", "了", "和", "也", "有", "就", "不", "人", "都", "而", "與", "或", "於", "及"}

# 定義分析的時間範圍（例如過去 7 天）
days_to_analyze = 7
start_date = datetime.now() - timedelta(days=days_to_analyze)

# 從資料庫中提取最近 7 天的文章
articles = list(news_collection.find({'published_time': {'$gte': start_date.strftime('%Y-%m-%d %H:%M:%S')}}))

# 計算 TF 和 DF
tf_per_doc = []  # 每篇文章的詞頻
df_counter = Counter()  # 文件頻率
total_documents = len(articles)

for article in articles:
    content = article.get('content', '')
    if content:
        # 使用 CKIP Transformers 對文章內容進行分詞
        words = ws_driver([content])[0]  # CKIP 返回的是嵌套列表，取第一個結果
        # 過濾掉過短的詞語和停用詞
        filtered_words = [word for word in words if len(word) > 1 and word not in stop_words]
        
        # 計算 TF
        tf = Counter(filtered_words)
        tf_per_doc.append(tf)
        
        # 更新 DF（每個詞只計算一次）
        unique_words = set(filtered_words)
        df_counter.update(unique_words)

# 計算 TF-IDF
tfidf_scores = defaultdict(float)
for doc_tf in tf_per_doc:
    for term, tf in doc_tf.items():
        # 計算 IDF
        idf = math.log(total_documents / (1 + df_counter[term]))  # 加 1 防止分母為 0
        # 計算 TF-IDF
        tfidf_scores[term] += tf * idf

# 排序 TF-IDF 分數
sorted_tfidf = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)

# 找出出現頻率最高的 10 個關鍵字
top_keywords = sorted_tfidf[:10]

# 輸出結果
print("近期熱門關鍵字（基於 TF-IDF）：")
for keyword, score in top_keywords:
    print(f"{keyword}: {score:.4f}")