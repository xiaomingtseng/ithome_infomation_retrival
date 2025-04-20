from gensim.models import Word2Vec
import numpy as np

class EmbeddedVector:
    def __init__(self, model_path=None):
        # 載入預訓練的詞嵌入模型
        if model_path:
            self.model = Word2Vec.load(model_path)
        else:
            self.model = None

    def train_model(self, tokenized_sentences, vector_size=100, window=5, min_count=1, workers=4):
        """
        訓練 Word2Vec 模型
        :param tokenized_sentences: 已斷詞的句子列表（每個句子是詞的列表）
        :param vector_size: 向量維度
        :param window: 上下文窗口大小
        :param min_count: 忽略出現次數少於 min_count 的詞
        :param workers: 執行緒數量
        """
        self.model = Word2Vec(sentences=tokenized_sentences, vector_size=vector_size, window=window, min_count=min_count, workers=workers)

    def save_model(self, model_path):
        """
        儲存訓練好的模型
        """
        if self.model:
            self.model.save(model_path)
        else:
            raise ValueError("模型尚未訓練或載入！")

    def get_word_vector(self, word):
        """
        獲取單詞的嵌入式向量
        :param word: 單詞
        :return: 詞向量（如果詞不存在於模型中，返回零向量）
        """
        if self.model and word in self.model.wv:
            return self.model.wv[word]
        else:
            return np.zeros(self.model.vector_size)

    def get_sentence_vector(self, sentence):
        """
        獲取句子的嵌入式向量（通過詞向量平均）
        :param sentence: 已斷詞的句子（詞列表）
        :return: 句子的嵌入式向量
        """
        if not self.model:
            raise ValueError("模型尚未訓練或載入！")

        vectors = [self.get_word_vector(word) for word in sentence if word in self.model.wv]
        if vectors:
            return np.mean(vectors, axis=0)
        else:
            return np.zeros(self.model.vector_size)