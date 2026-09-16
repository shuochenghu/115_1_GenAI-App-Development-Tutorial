# Week 8 AI Summarizer Demo

這是第 8 週期中個人小專題的教師示範範例。它展示一個完整 Streamlit App 應如何串接 OpenAI Responses API、Structured Outputs、錯誤處理與結果顯示。

## 功能

- 將長文整理成摘要。
- 產生重點、關鍵字與待辦事項。
- 使用 JSON Schema 要求模型回傳 structured output。
- 將 JSON 結果轉成使用者容易閱讀的 Streamlit 畫面。
- 支援貼上文字或上傳 `.txt` / `.md` 檔案。
- 可選擇同時顯示一段式 streaming 摘要，作為加分功能示範。
- 支援本機 `.env` 與 Streamlit Secrets。

## 安裝

課堂採 Python **3.12**（本次測試為 **3.12.13**）。以下指令從本 App 資料夾執行；從課程 repo 開啟時，先進入 `week08/week08_midterm_example_summarizer`。

請先在本專案資料夾建立虛擬環境，讓第 8 週 demo 的套件和其他週次專案分開管理。

Windows PowerShell：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
```

macOS / Linux：

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
```

## 設定 API Key

本機開發請複製 `.env.example` 成 `.env`：

```text
OPENAI_API_KEY=你的OpenAIAPIKey
OPENAI_MODEL=gpt-5.4-mini
```

部署時請改用 Streamlit Secrets。不要把 `.env` 或 `.streamlit/secrets.toml` 上傳到 GitHub。

## 執行

```bash
python -m streamlit run app.py
```

## Structured Output 欄位

| 欄位 | 說明 |
|---|---|
| `title` | 摘要結果標題 |
| `summary` | 2 到 4 句核心摘要 |
| `key_points` | 重要重點列表 |
| `keywords` | 關鍵字列表 |
| `action_items` | 後續行動或待辦事項 |

## Structured Outputs 的錯誤分流

`summarize_text()` 收到 API 回應後，先檢查 `output` 的拒答內容與 `response.status`；只有完成的回應才會進入空文字檢查與 `json.loads()`。Streamlit 會將這些情況顯示為簡短錯誤，而不呈現未完成的摘要。

| 情況 | 教師 demo 顯示的提示 |
|---|---|
| 模型拒答 | 說明此次未產生摘要資料，並顯示拒答原因 |
| `incomplete` | 區分輸出長度限制、內容過濾與其他未完成原因 |
| 空 `output_text` | 提醒稍後再試或縮短輸入 |
| JSON 無法解析 | 提醒檢查 schema 或模型設定 |

可用假的 API 回應示範這四個分支；真實 API 的拒答與未完成情況仍需上課前用測試環境確認。

## 教學提醒

這個範例是完成度參考，不建議學生直接照抄作為期中專題。學生應該修改題目、prompt、schema、輸入欄位、輸出呈現方式與 README。

正式主線仍以 JSON Schema + `strict` 示範 structured output。Pydantic `responses.parse()` 可作為進階選項，但學生不必為了期中專題改用 Pydantic。

API key 只能放在本機 `.env` 或 Streamlit Secrets，不能寫死在程式碼、README 或任何會上傳 GitHub 的檔案中。

## 啟動位置與 Community Cloud 部署

先啟用已安裝套件的 Python 3.12 虛擬環境，再選擇一種方式：

| 使用方式 | 啟動指令／Main file path |
|---|---|
| 本機：工作目錄是本 App 資料夾 | `python -m streamlit run app.py` |
| 本機：工作目錄是整個課程 repo 根目錄 | `python -m streamlit run week08/week08_midterm_example_summarizer/app.py` |
| 雲端：使用整個課程 repo | Main file path：`week08/week08_midterm_example_summarizer/app.py` |
| 雲端：把本 App 資料夾內容獨立成 repo | Main file path：`app.py` |

本 App 未提供自訂 `.streamlit/config.toml`，使用 Streamlit 預設設定。
`requirements.txt` 與 `app.py` 保持同一目錄；獨立成 repo 時也要保留 helper、範例資料與現有 `.streamlit` 範例檔。

在 Community Cloud 部署的 Advanced settings 選擇 **Python 3.12**，把 `.streamlit/secrets.example.toml` 的設定填入平台 Secrets；本機則使用 `.env` 或 `.streamlit/secrets.toml`。真實金鑰檔不可提交。

完整 Windows 課堂快照、設定優先順序、Colab 差異與部署檢核，見[課堂環境與部署指南](../../docs/課堂環境與部署指南.md)。若把 App 獨立成 repo，請一併保留指南副本或改成原課程 repo 的文件連結。
本次已測本機離線流程；實際 Community Cloud 安裝、瀏覽器互動與付費 API 仍待上課前確認。
