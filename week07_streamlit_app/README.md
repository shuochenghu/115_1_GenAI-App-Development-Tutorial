# Week 7 Streamlit AI App

這是「生成式AI應用開發」第 7 週範例專案，示範如何把 OpenAI Responses API 功能做成 Streamlit Web App。

## 功能

- 聊天介面
- Streaming 回覆
- Session state 聊天紀錄
- 摘要表單
- 文字檔上傳摘要
- `.env` / Streamlit Secrets API key 管理

## 安裝與執行

```bash
pip install -r requirements.txt
streamlit run app.py
```

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
| OpenAI helper | `app.py` | `create_client()`、`ask_ai()`、`stream_ai()` |
| Session State / Chat UI | `app.py` | `st.session_state`、`st.chat_input()`、`st.chat_message()` |
| Streaming | `app.py` | `stream=True`、`response.output_text.delta`、`st.write_stream()` |
| 表單與檔案上傳 | `app.py` | `tab_summary`、`tab_file` |
| 專案檢查 | `.gitignore`、`README.md` | 保護 `.env` 並說明專案執行方式 |

建議上課時一邊看 notebook，一邊在 VS Code 修改本資料夾檔案，並用 `streamlit run app.py` 測試。