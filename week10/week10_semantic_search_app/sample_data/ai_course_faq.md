# 生成式 AI 應用開發 FAQ

## Week 9 文件處理

第 9 週把 PDF、Word、CSV、TXT 與 Markdown 轉成文字，並做清理與 chunking。掃描 PDF 沒有文字層，需要 OCR 才能抽取內容。

## Week 10 Embedding 與語意搜尋

第 10 週把 chunks 轉成 embedding，使用 cosine similarity 找出與問題最相近的片段。本週只做 retrieval，不直接生成答案。

## Week 11 RAG

第 11 週會把搜尋到的片段組合成 context，再交給模型回答問題，並加入來源引用與基本評估。

## API key 安全

API key 必須放在環境變數、`.env` 或 Streamlit Secrets，不可以寫入程式碼，也不可以推送到 GitHub。

## 向量資料庫

ChromaDB 適合教學與小型原型，能把向量、文字與 metadata 放在一起。FAISS 搜尋速度快，但通常需要自己管理文件文字與 metadata 對照，Windows 安裝也較容易遇到問題。
