from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger
from database import Database
import nltk
from nltk.corpus import stopwords as nltk_stopwords  # 避免名稱衝突
from nltk.tokenize import word_tokenize
from nltk import pos_tag

# 確保 NLTK 資料已下載
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

class TextAnalyzer:
    def __init__(self, allowed_pos=None):
        self.allowed_pos = allowed_pos if allowed_pos else {
            "chinese": ["Na", "Nb", "Nc", "Nd", "Ncd", "VA"],
            "english": {"NN", "NNS", "NNP", "NNPS", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "JJ", "JJR", "JJS"}
        }
        self.ws_driver = CkipWordSegmenter(model="bert-base")  # 初始化 CKIP 分詞器

    def tokenize(self, text):
        """
        對文本進行斷詞
        """
        if not text.strip():
            return []
        return self.ws_driver([text])[0]  # 返回斷詞結果

    def collect_stopwords_by_pos(self, text):
        # 初始化 CKIP 詞性標註器
        pos_driver = CkipPosTagger(model="bert-base")
        
        # 斷詞與詞性標註
        word_segments = self.tokenize(text)
        if not word_segments:  # 如果斷詞結果為空，直接返回空列表
            return []
        
        pos_tags = pos_driver([word_segments])
        
        # 收集停用詞（不符合允許的詞性規則）
        stopwords = []
        for word, pos in zip(word_segments, pos_tags[0]):
            if pos not in self.allowed_pos["chinese"]:  # 如果詞性不在允許的列表中，則視為停用詞
                stopwords.append(word)
        
        return stopwords

    def collect_english_stopwords(self, text):
        # 使用 NLTK 處理英文部分
        english_stopwords = set(nltk_stopwords.words('english'))  # 使用改名後的 stopwords
        words = word_tokenize(text)
        
        # 詞性標註
        tagged_words = pos_tag(words)
        
        # 收集停用詞（不符合允許的詞性規則或是英文停用詞）
        stopwords = [
            word for word, pos in tagged_words 
            if pos not in self.allowed_pos["english"] or word.lower() in english_stopwords
        ]
        
        return stopwords

    def preprocess(self, content):
        """
        對文本進行斷詞，並過濾停用詞和標點符號
        """
        # 分離中文與英文部分
        chinese_text = ''.join([char for char in content if '\u4e00' <= char <= '\u9fff'])
        english_text = ''.join([char for char in content if char.isascii()])

        # 如果中文或英文部分為空，直接返回空列表
        if not chinese_text.strip() and not english_text.strip():
            return []

        # 收集斷詞結果
        chinese_tokens = self.tokenize(chinese_text)
        english_tokens = word_tokenize(english_text)

        # 過濾停用詞
        chinese_stopwords = self.collect_stopwords_by_pos(chinese_text)
        english_stopwords = self.collect_english_stopwords(english_text)

        # 過濾標點符號
        chinese_tokens = [word for word in chinese_tokens if word not in "，。、；：「」『』（）《》〈〉【】——……！￥？"]
        english_tokens = [word for word in english_tokens if word.isalnum()]

        # 過濾停用詞後的結果
        filtered_tokens = [word for word in chinese_tokens if word not in chinese_stopwords] + \
                          [word for word in english_tokens if word not in english_stopwords]

        return filtered_tokens

def fetch_article_from_db():
    # 初始化資料庫連線
    db_instance = Database()
    news_collection = db_instance.get_collection('news')
    
    # 從資料庫中取得一篇文章（假設有 'content' 欄位）
    article = news_collection.find_one({}, {"content": 1})
    return article['content'] if article else None

def save_to_txt(filename, content):
    # 去重並排序停用詞
    unique_content = sorted(set(content))
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("\n".join(unique_content))

if __name__ == "__main__":
    # 從資料庫中取得文章
    article = fetch_article_from_db()
    if not article:
        print("無法從資料庫中取得文章。")
    else:
        # 初始化分析器，動態設定允許的詞性規則
        analyzer = TextAnalyzer(allowed_pos={
            "chinese": ["Na", "Nb", "Nc", "Nd", "Ncd", "VA"],  # 中文允許的詞性
            "english": {"NN", "NNS", "NNP", "NNPS", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "JJ", "JJR", "JJS"}  # 英文允許的詞性
        })
        
        # 分離中文與英文部分
        chinese_text = ''.join([char for char in article if '\u4e00' <= char <= '\u9fff'])
        english_text = ''.join([char for char in article if char.isascii()])

        # 收集中文停用詞
        chinese_stopwords = analyzer.collect_stopwords_by_pos(chinese_text)

        # 收集英文停用詞
        english_stopwords = analyzer.collect_english_stopwords(english_text)

        # 合併中文與英文停用詞
        combined_stopwords = chinese_stopwords + english_stopwords

        # 將結果存入同一份檔案
        save_to_txt("stopwords.txt", combined_stopwords)
        print("停用詞已儲存至 stopwords.txt")