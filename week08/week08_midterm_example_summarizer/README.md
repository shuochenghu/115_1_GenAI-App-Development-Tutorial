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

```bash
pip install -r requirements.txt
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
streamlit run app.py
```

## Structured Output 欄位

| 欄位 | 說明 |
|---|---|
| `title` | 摘要結果標題 |
| `summary` | 2 到 4 句核心摘要 |
| `key_points` | 重要重點列表 |
| `keywords` | 關鍵字列表 |
| `action_items` | 後續行動或待辦事項 |

## 教學提醒

這個範例是完成度參考，不建議學生直接照抄作為期中專題。學生應該修改題目、prompt、schema、輸入欄位、輸出呈現方式與 README。

正式主線仍以 JSON Schema + `strict` 示範 structured output。Pydantic `responses.parse()` 可作為進階選項，但學生不必為了期中專題改用 Pydantic。

API key 只能放在本機 `.env` 或 Streamlit Secrets，不能寫死在程式碼、README 或任何會上傳 GitHub 的檔案中。
