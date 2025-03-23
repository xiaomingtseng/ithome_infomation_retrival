from datetime import datetime, timedelta
from collections import Counter
from database import Database
from ckip_transformers.nlp import CkipWordSegmenter

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
articles = news_collection.find({'published_time': {'$gte': start_date.strftime('%Y-%m-%d %H:%M:%S')}})

# 分詞並統計關鍵字頻率
word_counter = Counter()
for article in articles:
    content = article.get('content', '')
    if content:
        # 使用 CKIP Transformers 對文章內容進行分詞
        words = ws_driver([content])[0]  # CKIP 返回的是嵌套列表，取第一個結果
        # 過濾掉過短的詞語和停用詞
        filtered_words = [word for word in words if len(word) > 1 and word not in stop_words]
        word_counter.update(filtered_words)

# 找出出現頻率最高的 10 個關鍵字
top_keywords = word_counter.most_common(10)

# 輸出結果
print("近期熱門關鍵字：")
for keyword, count in top_keywords:
    print(f"{keyword}: {count}")