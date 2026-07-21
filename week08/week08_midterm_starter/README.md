# Week 8 Midterm Starter

這是第 8 週期中個人小專題的學生 starter。請把它複製成自己的專題資料夾，再依照 `app.py` 裡的 TODO 改造成你的 App。

## 功能目標

這份 starter 已經提供：

- Streamlit 基本頁面。
- `.env` 與 Streamlit Secrets 雙軌設定。
- OpenAI Responses API helper。
- Structured Outputs 範例 schema。
- 可選 streaming helper，作為加分功能骨架。
- 基本輸入檢查與錯誤提示。
- 結果顯示區與原始 JSON 檢視。

## 快速開始

```bash
pip install -r requirements.txt
```

本機開發請複製 `.env.example` 成 `.env`：

```powershell
Copy-Item .env.example .env
```

macOS / Linux：

```bash
cp .env.example .env
```

然後在 `.env` 填入：

```text
OPENAI_API_KEY=你的OpenAIAPIKey
OPENAI_MODEL=gpt-5.4-mini
```

部署到 Streamlit Community Cloud 時，請把相同設定放到 Streamlit Secrets。不要把 `.env` 或 `.streamlit/secrets.toml` 上傳到 GitHub。

## 執行

```bash
streamlit run app.py
```

尚未填 `OPENAI_API_KEY` 也可以開啟畫面，App 會顯示提醒；填好 key 後才會實際呼叫 API。

## 你需要完成的 TODO

- 修改 `PROJECT_TITLE` 與 `PROJECT_DESCRIPTION`。
- 改寫 `SYSTEM_PROMPT`。
- 依你的專題設計 `DEFAULT_SCHEMA`。
- 在 `build_prompt()` 中設計任務指令。
- 修改 `render_project_form()` 的欄位。
- 調整 `render_structured_result()` 的顯示方式。
- 選做：把 `stream_ai()` 搭配 `st.write_stream()` 加入結果區，作為 streaming 加分功能。
- 補完自己的 README。

## 繳交前檢查

- [ ] App 可以用 `streamlit run app.py` 執行。
- [ ] 至少一個功能會呼叫 OpenAI API。
- [ ] 至少一個功能使用真 structured output，不是只在 prompt 中要求「請用 JSON 回答」。
- [ ] `.env` 沒有上傳到 GitHub。
- [ ] README 說明專題目的、安裝方式、執行方式、輸出格式與限制。

## 安全紅線

API key 只能放在本機 `.env` 或 Streamlit Secrets。不得寫死在 `app.py`、README、notebook 或任何會上傳 GitHub 的檔案中。
