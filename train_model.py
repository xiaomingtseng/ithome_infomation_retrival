from database import Database
from text_analyzer import TextAnalyzer
from embedded_vector import EmbeddedVector

# 初始化資料庫
db_instance = Database()
news_collection = db_instance.get_collection('news')

# 初始化斷詞器
analyzer = TextAnalyzer()

# 從資料庫中提取所有文章
articles = list(news_collection.find({}))

# 收集所有文章的斷詞結果
tokenized_sentences = []
for article in articles:
    content = article.get('content', '')
    if not content.strip():  # 如果文章內容為空或僅包含空白字符，跳過
        continue

    tokens = analyzer.preprocess(content)  # 使用 TextAnalyzer 進行斷詞和停用詞過濾
    tokenized_sentences.append(tokens)

print(f"已處理 {len(tokenized_sentences)} 篇文章")

# 初始化嵌入式向量處理器
embedder = EmbeddedVector()

# 訓練模型
embedder.train_model(tokenized_sentences, vector_size=100, window=5, min_count=1, workers=4)

# 儲存模型
embedder.save_model("custom_word2vec.model")
print("詞嵌入模型已儲存為 custom_word2vec.model")