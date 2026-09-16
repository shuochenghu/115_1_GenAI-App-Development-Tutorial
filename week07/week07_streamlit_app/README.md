# Week 7 Streamlit AI App

這是「生成式AI應用開發」第 7 週範例專案，示範如何把 OpenAI Responses API 功能做成 Streamlit Web App。

## 功能

- 聊天介面；API 會收到最近五輪已完成的對話與本輪問題
- Streaming 回覆；只有收到完成事件才保存正式聊天紀錄
- Session state 聊天紀錄與清空功能
- 摘要表單
- 文字檔上傳摘要
- `.env` / Streamlit Secrets API key 管理

## 安裝與執行

以下從本 App 資料夾執行；若剛開啟整個課程 repo，先進入 `week07/week07_streamlit_app`。
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

## 環境變數

本機開發請建立 `.env`：

```env
OPENAI_API_KEY=你的key
OPENAI_MODEL=gpt-5.4-mini
```

部署到 Streamlit Community Cloud 時，請在 App Settings 的 Secrets 中設定：

```toml
OPENAI_API_KEY = "你的key"
OPENAI_MODEL = "gpt-5.4-mini"
```

## 聊天功能怎麼測

1. 在「聊天」分頁問「第 7 週主要學什麼？」；再追問「剛才那一週要用什麼工具？」。第二輪應能利用第一輪的脈絡回答。
2. 點「清空聊天紀錄」後再問「剛才那一週要用什麼工具？」；新對話不應知道已清空的前文。
3. 聊天只帶入最近五輪已完成的 user／assistant 訊息，避免前文無限制增加成本。摘要表單和檔案工具不會帶入聊天紀錄。
4. 如果 API 或串流中斷，畫面會顯示錯誤；這輪 user 問題與部分回答都不會存入正式聊天紀錄。

## 安全提醒

- 不要把 `.env` 或 `.streamlit/secrets.toml` 推上 GitHub。
- 不要上傳個資、機密文件或敏感資料。
- API 會產生成本，測試時請控制輸入長度與使用次數。
## 與 notebook 教材的對照

第 7 週 notebook 是教材與步驟導引；本資料夾是實際執行的 VS Code 專案。

| Notebook 章節 | 本專案檔案 | 對應內容 |
|---|---|---|
| 本機環境準備 | `requirements.txt` | 安裝 Streamlit、OpenAI SDK、python-dotenv |
| API Key 管理 | `.env.example`、`app.py` | 使用 `.env` 或 Streamlit Secrets，不把 API key 寫死 |
| OpenAI helper | `app.py` | `create_client()`、`build_chat_input()`、`ask_ai()`、`stream_ai()` |
| Session State / Chat UI | `app.py` | 已完成的聊天紀錄送進 API、`st.chat_input()`、`st.chat_message()` |
| Streaming | `app.py` | `response.output_text.delta`、`response.completed`、錯誤分流、`st.write_stream()` |
| 表單與檔案上傳 | `app.py` | `tab_summary`、`tab_file` |
| 專案檢查 | `.gitignore`、`README.md` | 保護 `.env` 並說明專案執行方式 |

建議上課時一邊看 notebook，一邊在 VS Code 修改本資料夾檔案，並用 `python -m streamlit run app.py` 測試。

## 啟動位置與 Community Cloud 部署

先啟用已安裝套件的 Python 3.12 虛擬環境，再選擇一種方式：

| 使用方式 | 啟動指令／Main file path |
|---|---|
| 本機：工作目錄是本 App 資料夾 | `python -m streamlit run app.py` |
| 本機：工作目錄是整個課程 repo 根目錄 | `python -m streamlit run week07/week07_streamlit_app/app.py` |
| 雲端：使用整個課程 repo | Main file path：`week07/week07_streamlit_app/app.py` |
| 雲端：把本 App 資料夾內容獨立成 repo | Main file path：`app.py` |

本 App 未提供自訂 `.streamlit/config.toml`，使用 Streamlit 預設設定。
`requirements.txt` 與 `app.py` 保持同一目錄；獨立成 repo 時也要保留 helper、範例資料與現有 `.streamlit` 範例檔。

在 Community Cloud 部署的 Advanced settings 選擇 **Python 3.12**，把 `.streamlit/secrets.example.toml` 的設定填入平台 Secrets；本機則使用 `.env` 或 `.streamlit/secrets.toml`。真實金鑰檔不可提交。

完整 Windows 課堂快照、設定優先順序、Colab 差異與部署檢核，見[課堂環境與部署指南](../../docs/課堂環境與部署指南.md)。若把 App 獨立成 repo，請一併保留指南副本或改成原課程 repo 的文件連結。
本次已測本機離線流程；實際 Community Cloud 安裝、瀏覽器互動與付費 API 仍待上課前確認。
