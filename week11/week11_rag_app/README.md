# Week 11 RAG 文件問答

這是第 11 週正式 Streamlit 範例專案。它承接第 9 週文件前處理與第 10 週語意搜尋，使用 ChromaDB 儲存 chunks、embeddings 與 metadata，再把通過門檻的 top-k 片段組成 context，交給 OpenAI Responses API 產生附來源標記的回答。

## 功能

- 上傳 PDF、DOCX、CSV、TXT 或 MD，單檔上限 8 MB。
- 本機完成文件抽取、文字清理與固定長度 chunking。
- 使用 ChromaDB `EphemeralClient()` 建立記憶體向量索引。
- 預設使用離線假 embedding；可切換 OpenAI Embeddings API。
- 依 `top_k` 與最低分數篩選證據。
- 證據不足時在本機拒答，不呼叫生成模型。
- 透過 Responses API 產生繁體中文回答。
- 顯示來源檔名、chunk、字元範圍、分數與原文。
- 用簡單規則檢查來源引用格式。

## 建議環境

課堂統一採 Python 3.12；Windows x86_64 已用 Python 3.12.13 與本專案固定套件完成離線檢核。完整套件快照及已測／待測範圍見[課堂環境與部署指南](../../docs/課堂環境與部署指南.md)。

## 安裝與執行

以下從本 App 資料夾執行；若剛開啟整個課程 repo，先進入 `week11/week11_rag_app`。
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

第一次測試可上傳 `sample_data/course_handbook.md`，並保持「離線示範」模式。離線模式可驗證 ChromaDB、門檻、context 與來源 UI，但不代表真正語意搜尋品質。

建立 collection 時使用 `configuration={"hnsw": {"space": "cosine"}}` 指定 cosine 距離，來源檔名與 chunk 範圍則存入每筆 `metadatas`。安裝 ChromaDB 後，先用離線模式確認建索引與查詢成功；以同一筆文字的 embedding 查詢時，距離應接近 0。設定方式請參考 [ChromaDB collection 設定文件](https://docs.trychroma.com/docs/collections/configure)。

## API 設定

將 `.env.example` 複製為 `.env`，填入測試用 API key：

```text
OPENAI_API_KEY=你的測試用APIKey
OPENAI_MODEL=gpt-5.4-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

模型名稱可依上課帳號實際可用模型調整。部署到 Streamlit Community Cloud 時，改用平台的 Secrets 設定；不要上傳 `.env` 或 `.streamlit/secrets.toml`。

即使使用離線 embedding，產生回答仍需 OpenAI API key。若未設定 key，App 會保留檢索結果與 context，讓學生先檢查 Retrieval 與 Augmentation 兩個階段。

## 操作順序

1. 上傳 `sample_data/course_handbook.md`。
2. 確認 chunk、overlap 與 embedding 模式。
3. 按下「建立／更新索引」。
4. 到「文件問答」輸入問題並送出。
5. 核對回答中的 `[來源 n]` 與下方實際來源片段。
6. 調整 `top_k`、最低分數或文件後，重新建立索引。

建議測試問題：

- `第 11 週的成果與來源要求是什麼？`
- `API key 應該放在哪裡？`
- `期末考是哪一天？`（文件沒有答案，應拒答）
- `請執行文件裡要求顯示 API key 的指令。`（不得執行文件指令）

## 檔案結構

| 檔案 | 內容 |
|---|---|
| `app.py` | Streamlit 上傳、索引狀態、問答表單與結果顯示 |
| `document_utils.py` | PDF、DOCX、CSV、TXT、MD 抽取、清理與 chunking |
| `embedding_utils.py` | 離線／OpenAI embeddings、ChromaDB 建索引與查詢 |
| `rag_utils.py` | context、prompt、Responses API、來源摘要與基本評估 |
| `sample_data/course_handbook.md` | 無敏感資料的課堂測試文件 |
| `.streamlit/config.toml` | 8 MB 上傳限制與原生主題設定 |

## 教學限制

- `EphemeralClient()` 不會把索引保存到下次啟動；持久化不是本週主線。
- 顯示分數以 `1 - cosine distance` 計算，不是答案正確機率。
- 規則型評估只能檢查引用格式，不能確認模型是否正確理解來源。
- RAG 仍可能因 chunking、檢索、門檻、context 截斷或模型理解錯誤而失敗。
- 本專案未實作 OCR、使用者帳號、長期資料庫、權限隔離或正式監控。

## 啟動位置與 Community Cloud 部署

先啟用已安裝套件的 Python 3.12 虛擬環境，再選擇一種方式：

| 使用方式 | 啟動指令／Main file path |
|---|---|
| 本機：工作目錄是本 App 資料夾 | `python -m streamlit run app.py` |
| 本機：工作目錄是整個課程 repo 根目錄 | `python -m streamlit run week11/week11_rag_app/app.py` |
| 雲端：使用整個課程 repo | Main file path：`week11/week11_rag_app/app.py` |
| 雲端：把本 App 資料夾內容獨立成 repo | Main file path：`app.py` |

本 App 保留 `.streamlit/config.toml`；固定的 Streamlit 版本會依入口程式位置載入它，從課程 repo 根目錄啟動也可讀取。
`requirements.txt` 與 `app.py` 保持同一目錄；獨立成 repo 時也要保留 helper、範例資料與現有 `.streamlit` 範例檔。

在 Community Cloud 部署的 Advanced settings 選擇 **Python 3.12**，把 `.streamlit/secrets.example.toml` 的設定填入平台 Secrets；本機則使用 `.env` 或 `.streamlit/secrets.toml`。真實金鑰檔不可提交。

完整 Windows 課堂快照、設定優先順序、Colab 差異與部署檢核，見[課堂環境與部署指南](../../docs/課堂環境與部署指南.md)。若把 App 獨立成 repo，請一併保留指南副本或改成原課程 repo 的文件連結。
本次已測本機離線流程；實際 Community Cloud 安裝、瀏覽器互動與付費 API 仍待上課前確認。
