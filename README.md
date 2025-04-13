# instragram_infomation_retrival
# 熱門關鍵字提取功能

本專案旨在實現一個高效的熱門關鍵字提取功能，支援中英文混合內容處理，並基於 CKIP 斷詞與 TF-IDF 演算法進行關鍵字分析。此外，還結合多種優化技術以提升準確性與效能。

## 功能特點

1. **中英文混合支持**：
   - 基於 CKIP 進行中文斷詞，並對英文進行分詞與處理。
   - 自動處理各種符號與雜訊。

2. **關鍵字提取**：
   - 使用 TF-IDF 提取熱門關鍵字。
   - 支援基於 n-gram 的短語提取。
   - 支援詞頻與共現分析。

3. **進階優化**：
   - 引入 TextRank 演算法進行排序。
   - 支援 LDA 主題建模，提取與主題相關的關鍵字。
   - 可選用詞嵌入技術（如 Word2Vec 或 Bert）進一步提升準確性。

4. **高效性能**：
   - 支援大規模文本的批次處理與並行計算。
   - 提供增量更新功能，避免重複計算。

5. **可視化**：
   - 生成詞雲圖、頻率直方圖等視覺化結果。

---

## 使用方式

### 環境需求

- Python 3.8+
- 安裝必要套件：
  ```bash
  pip install -r requirements.txt
  ```

### 基本使用範例

1. **輸入文本**：
   - 將需要分析的文本存入一個 `.txt` 檔案。

2. **執行提取腳本**：
   ```bash
   python extract_keywords.py --input texts/sample.txt --output results/keywords.json
   ```

3. **結果格式**：
   - 關鍵字結果將輸出為 JSON 檔案，範例如下：
     ```json
     {
       "keywords": [
         {"word": "人工智能", "score": 0.85},
         {"word": "機器學習", "score": 0.72},
         {"word": "深度學習", "score": 0.65}
       ]
     }
     ```

---

## 文件結構

```plaintext
.
├── texts/                     # 存放原始輸入文本
├── results/                   # 存放分析結果
├── extract_keywords.py        # 核心關鍵字提取腳本
├── requirements.txt           # 所需 Python 套件列表
└── README.md                  # 使用說明文件
```

---

## 進階使用

### 自訂停用詞表
可在 `data/stopwords.txt` 中添加或修改停用詞，避免無意義詞彙出現在結果中。

### 調整參數
在執行腳本時可透過命令列參數自訂相關選項：
- `--ngram`：設定 n-gram 模型的範圍（預設為 1~2）。
- `--top-k`：設定提取的關鍵字數量（預設為 10）。

範例如下：
```bash
python extract_keywords.py --input texts/sample.txt --ngram 1 2 --top-k 15
```

---

## TODO

- [ ] 增加情感分析功能，提取與情感相關的熱門關鍵字。
- [ ] 增強多語言支持，處理更多語言的文本。
- [ ] 提供 Web 介面，方便使用者即時輸入與查看結果。

---

## 貢獻指南

歡迎貢獻代碼或提出改進建議！請參考以下步驟：

1. Fork 本專案。
2. 創建新分支進行修改。
3. 提交 Pull Request。

---

## 聯繫方式

如有任何問題，請透過 [issues 區](https://github.com/xiaomingtseng/hot-keywords/issues) 或直接聯繫我。