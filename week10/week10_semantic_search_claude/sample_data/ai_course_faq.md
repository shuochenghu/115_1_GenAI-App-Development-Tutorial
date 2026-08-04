# 生成式 AI 應用開發 課程 FAQ（語意搜尋測試用）

## 課程平台
本課程主線使用 OpenAI API，補充比較 Claude 與 Gemini。
Web App 一律用 Streamlit 開發與部署。

## Embedding 是什麼
Embedding 是把一段文字轉換成一串數字向量。語意相近的文字，向量方向也相近。
它不是摘要、不是分類、也不是資料庫，而是「讓電腦能比較語意」的表示法。

## 語意搜尋和關鍵字搜尋差在哪
關鍵字搜尋比對字面是否相同，換個講法就找不到。
語意搜尋比對向量的相似度，即使用不同詞句，只要意思接近就能找到。

## 向量資料庫
向量資料庫（例如 ChromaDB）會把向量、原文與 metadata 存在一起，
支援快速的 top-k 相似度查詢與條件過濾，適合作為 RAG 的檢索層。

## 成本與安全
呼叫 Embeddings API 會依文字長度計費，建議批次處理並限制輸入長度。
API key 只能放在環境變數、.env 或 Streamlit Secrets，不可寫死在程式碼或上傳 GitHub。

## 期末專題
期末專題需要一個可部署的 Streamlit Web App，至少一種外部資料來源，
並包含 RAG 或 Function Calling 其中一項，附 GitHub repo、README 與可部署網址。
