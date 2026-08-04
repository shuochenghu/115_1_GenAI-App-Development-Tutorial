# Week 10 Embedding 與語意搜尋

這是第 10 週正式 Streamlit 範例專案。它承接第 9 週文件處理管線，將文件切成 chunks，再把 chunks 轉成 embedding，用 cosine similarity 找出與查詢最相近的片段。

本週只做 retrieval，也就是「找相關片段」；第 11 週才會把搜尋結果組成 context 並交給模型產生 RAG 答案。

## 功能

- 上傳 PDF、DOCX、CSV、TXT、MD。
- 沿用第 9 週 reader、文字清理與 chunking。
- 預設使用離線假 embedding，不需 API key 即可跑完整流程。
- 可切換成 OpenAI Embeddings API 產生真語意向量。
- 用 cosine similarity 搜尋 top-k 相近片段。
- 顯示 chunk 來源、字元範圍與相似度。
- App 與 Streamlit 設定都限制單檔上傳大小為 8 MB。

## 安裝與執行

```bash
cd week10/week10_semantic_search_app
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

未設定 API key 時，請保持「離線示範模式」開啟；它能驗證文件處理、chunking、向量索引與搜尋 UI，但沒有真正語意。

## API 設定

複製 `.env.example` 為 `.env`：

```text
OPENAI_API_KEY=你的測試用APIKey
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

部署時使用 Streamlit Secrets。不得將 `.env`、`.streamlit/secrets.toml` 或真實 API key 推送到 GitHub。

## 檔案結構

| 檔案 | 內容 |
|---|---|
| `app.py` | Streamlit UI、索引建立按鈕、搜尋表單與結果顯示 |
| `document_utils.py` | 第 9 週文件抽取、清理、chunking；全都在本機執行 |
| `embedding_utils.py` | 離線假 embedding、OpenAI Embeddings、cosine similarity、最小搜尋索引 |
| `requirements.txt` | Streamlit、OpenAI SDK、NumPy 與文件 reader 相關套件 |
| `.env.example` | 本機 API key 設定範本；真正的 `.env` 不可上傳 |
| `.streamlit/secrets.example.toml` | Streamlit Community Cloud Secrets 範本 |
| `.streamlit/config.toml` | Streamlit 專案設定，目前限制上傳檔案大小為 8 MB |
| `sample_data/ai_course_faq.md` | 無敏感資料的測試文件 |

## ChromaDB 與 FAISS 放在哪裡？

正式 App 先用 `list[dict]` + NumPy 做最小語意搜尋，因為這最容易觀察資料流，也最適合教室環境。正式 notebook 另提供「ChromaDB preview」選讀 cell，可用 `chromadb.EphemeralClient()` 建立 in-memory collection、加入 embeddings 與 metadata、再查詢 top-k 結果。

ChromaDB 沒有列入正式 App 的必要 `requirements.txt`。若要執行 notebook 選讀 preview，請在 notebook 或虛擬環境中另外安裝：

```bash
pip install chromadb
```

FAISS 速度快，但需要自行管理原文與 metadata 對照，Windows 安裝也較容易卡住，因此列為自主學習補充。

## 建議測試

1. 上傳 `sample_data/ai_course_faq.md`。
2. 保持離線示範模式，建立索引並搜尋「第 11 週會做什麼」。
3. 調整 `chunk_size` 與 `top_k`，觀察結果排序變化。
4. 設定測試用 API key 後，關閉離線示範模式，再建立索引觀察真語意搜尋效果。
