import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

def extract_keywords_with_textrank(embedder, tokens, top_k=10):
    """
    使用 TextRank 提取關鍵字
    """
    word_vectors = np.array([embedder.get_word_vector(word) for word in tokens if word in embedder.model.wv])
    similarity_matrix = cosine_similarity(word_vectors)

    # 建立圖結構
    graph = nx.from_numpy_array(similarity_matrix)
    scores = nx.pagerank(graph)

    # 排序並選擇前 K 個關鍵字
    ranked_words = sorted(((tokens[i], score) for i, score in scores.items()), key=lambda x: x[1], reverse=True)
    return [word for word, score in ranked_words[:top_k]]