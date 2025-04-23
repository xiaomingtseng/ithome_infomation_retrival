from text_analyzer import TextAnalyzer
from tf_idf import TFIDFAnalyzer
from embedded_vector import EmbeddedVector
from sklearn.cluster import KMeans
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from database import Database

def extract_keywords_with_tfidf(tfidf_analyzer, articles, top_k=10):
    """
    使用 TF-IDF 提取關鍵字
    """
    tfidf_scores = tfidf_analyzer.compute_tfidf(articles)
    return [word for word, score in tfidf_scores[:top_k]]

def extract_keywords_with_kmeans(embedder, tokens, n_clusters=3):
    """
    使用 KMeans 聚類提取關鍵字
    """
    # 獲取詞向量
    word_vectors = np.array([embedder.get_word_vector(word) for word in tokens if word in embedder.model.wv])
    
    # 如果詞向量為空，直接返回空列表
    if len(word_vectors) == 0:
        print("警告：詞向量為空，無法進行 KMeans 聚類")
        return []

    # 調整聚類數量
    if len(word_vectors) < n_clusters:
        n_clusters = len(word_vectors)

    # 使用 KMeans 聚類
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(word_vectors)

    # 找到每個聚類中心最近的詞
    keywords = []
    for i in range(n_clusters):
        cluster_center = kmeans.cluster_centers_[i]
        closest_word = min(tokens, key=lambda word: np.linalg.norm(embedder.get_word_vector(word) - cluster_center))
        keywords.append(closest_word)

    return keywords

if __name__ == "__main__":
    # 初始化資料庫
    db_instance = Database()
    news_collection = db_instance.get_collection('news')
    articles = list(news_collection.find({}))

    # 初始化斷詞器
    analyzer = TextAnalyzer()

    # 載入自訓練的詞嵌入模型
    embedder = EmbeddedVector(model_path="custom_word2vec.model")

    for article in articles:
        content = article.get('content', '')
        if not content:
            continue

        # 使用 TextAnalyzer 過濾停用詞並斷詞
        tokens = analyzer.preprocess(content)
        # print("過濾後的 tokens:", tokens)

        tf_idf_keywords = extract_keywords_with_tfidf(
            TFIDFAnalyzer(), [{'content': content}], top_k=10
        )

        

        # print(f"TF-IDF 關鍵字(前10)：{tf_idf_keywords}")
        # print("-" * 50)

        # 使用 KMeans 提取關鍵字（2~3 個）
        kmeans_keywords = extract_keywords_with_kmeans(embedder, tokens, n_clusters=10)

        # 將結果寫入 .txt 檔案
        with open("kmeans_keywords.txt", "a", encoding="utf-8") as f:
            f.write(f"文章內容：{content[:50]}...\n")
            f.write(f"KMeans 關鍵字：{', '.join(kmeans_keywords)}\n")
            f.write("-" * 50 + "\n")

        # 輸出結果
        print(f"文章內容：{content[:50]}...")
        print(f"KMeans 關鍵字：{kmeans_keywords}")
        print("-" * 50)