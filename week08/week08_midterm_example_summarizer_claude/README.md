# AI 摘要器（教師 demo 範例，Claude 版）

> 這是第 8 週期中專題的**完成度參考範例**，用來讓學生看到「一個做完的專題長什麼樣」。
> ⚠️ 學生**不可**直接繳交本範例；你的專題必須有自己的題目、prompt、輸出欄位與 README。

---

## 專題簡介

把長文、課堂筆記或會議記錄貼上（或上傳 `.txt` / `.md`），一鍵產生**結構化摘要**：標題、重點、關鍵字、待辦事項。目標使用者是需要快速抓重點的學生或上班族。

## 功能

- 兩種輸入：貼上文字 或 上傳 `.txt` / `.md` 檔
- 結構化摘要（Pydantic + `responses.parse()`）：標題 / 摘要 / 重點 / 關鍵字 / 待辦
- 加分：一段式**串流**摘要（`st.write_stream`）
- 安全與健壯性：API key 缺失提示、輸入驗證、輸入長度上限、錯誤處理

## 安裝方式

```bash
pip install -r requirements.txt
```

## 環境變數設定

複製 `.env.example` 為 `.env`，填入：

```
OPENAI_API_KEY=你的_key
OPENAI_MODEL=gpt-5.4-mini
```

## 執行方式

```bash
streamlit run app.py
```

## 使用流程

1. 在「貼上文字」貼上內容，或在「上傳檔案」上傳 `.txt` / `.md`。
2. （可選）開啟「一段式串流摘要」示範串流輸出。
3. 按「產生摘要」，即可看到結構化結果與原始 JSON。

## AI 輸出格式（結構化欄位）

| 欄位 | 型態 | 用途 |
|---|---|---|
| `title` | str | 文件短標題 |
| `summary` | str | 3–4 句整體重點 |
| `key_points` | list[str] | 3–6 個重點 |
| `keywords` | list[str] | 3–8 個關鍵字 |
| `action_items` | list[str] | 待辦事項；無則為空陣列 |

## 限制與安全提醒

- AI 摘要可能遺漏或誤解重點，重要用途請人工複核。
- 請勿上傳含個資或機密的文件。
- 輸入上限 12000 字，避免單次成本過高。
- API key 只能放 `.env` 或 Streamlit Secrets，**不可寫死或推上 GitHub**。
