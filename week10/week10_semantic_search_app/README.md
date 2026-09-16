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
- 上傳元件明訂 `max_upload_size=8`，收檔後再檢查 8 MB 上限；`.streamlit/config.toml` 也保留相同預設。

## 安裝與執行

以下從本 App 資料夾執行；若剛開啟整個課程 repo，先進入 `week10/week10_semantic_search_app`。
課堂採 Python **3.12**，本次測試版本為 **3.12.13**。

Windows PowerShell：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
python -m streamlit run app.py
```

macOS / Linux（需先安裝 Python 3.12）：

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
python -m streamlit run app.py
```

`requirements.txt` 固定直接依賴；若要重現整組已測教室環境，請依[課堂環境與部署指南](../../docs/課堂環境與部署指南.md)使用完整 Windows 快照。macOS／Linux 與 Community Cloud 仍需在目標環境驗證。

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
python -m pip install -r requirements-chroma.txt
```

ChromaDB preview 與選讀 helper 建立 collection 時使用 `configuration={"hnsw": {"space": "cosine"}}` 指定 cosine 距離；每個 chunk 的來源資料仍放在 `metadatas`。安裝後可在正式 Notebook 執行 preview cell，確認建立 collection、加入向量與 `query()` 都成功；相同向量的查詢距離應接近 0。設定方式請參考 [ChromaDB collection 設定文件](https://docs.trychroma.com/docs/collections/configure)。

FAISS 速度快，但需要自行管理原文與 metadata 對照，Windows 安裝也較容易卡住，因此列為自主學習補充。

## 建議測試

1. 上傳 `sample_data/ai_course_faq.md`。
2. 保持離線示範模式，建立索引並搜尋「第 11 週會做什麼」。
3. 調整 `chunk_size` 與 `top_k`，觀察結果排序變化。
4. 設定測試用 API key 後，關閉離線示範模式，再建立索引觀察真語意搜尋效果。

## 啟動位置與 Community Cloud 部署

先啟用已安裝套件的 Python 3.12 虛擬環境，再選擇一種方式：

| 使用方式 | 啟動指令／Main file path |
|---|---|
| 本機：工作目錄是本 App 資料夾 | `python -m streamlit run app.py` |
| 本機：工作目錄是整個課程 repo 根目錄 | `python -m streamlit run week10/week10_semantic_search_app/app.py` |
| 雲端：使用整個課程 repo | Main file path：`week10/week10_semantic_search_app/app.py` |
| 雲端：把本 App 資料夾內容獨立成 repo | Main file path：`app.py` |

本 App 保留 `.streamlit/config.toml`；固定的 Streamlit 版本會依入口程式位置載入它，從課程 repo 根目錄啟動也可讀取。
`requirements.txt` 與 `app.py` 保持同一目錄；獨立成 repo 時也要保留 helper、範例資料與現有 `.streamlit` 範例檔。

在 Community Cloud 部署的 Advanced settings 選擇 **Python 3.12**，把 `.streamlit/secrets.example.toml` 的設定填入平台 Secrets；本機則使用 `.env` 或 `.streamlit/secrets.toml`。真實金鑰檔不可提交。

完整 Windows 課堂快照、設定優先順序、Colab 差異與部署檢核，見[課堂環境與部署指南](../../docs/課堂環境與部署指南.md)。若把 App 獨立成 repo，請一併保留指南副本或改成原課程 repo 的文件連結。
本次已測本機離線流程；實際 Community Cloud 安裝、瀏覽器互動與付費 API 仍待上課前確認。
