# 生成式AI應用開發 第 08 週 期中個人小專題（Claude 版）

> 平台：OpenAI API + Streamlit + GitHub
> 定位：整合第 3–7 週能力，個人完成一個可展示的小型 LLM Web App。
> 佔學期成績 20%。
> 對應範本：`week08_midterm_starter_claude/`（起始骨架）、`week08_midterm_example_summarizer_claude/`（教師 demo 範例）。

---

## 一、本週目標

第 8 週不是新 API 教學，而是把前面幾週的能力整合成一個小型專題。完成後你應能：

1. 用 Streamlit 建立可操作的 AI Web App。
2. 用 OpenAI Responses API 完成一個明確任務。
3. 設計 structured output，讓 AI 結果能被程式穩定讀取。
4. 用 `.env` / Streamlit Secrets 管理 API key。
5. 建立 GitHub repository，並用 README 說明專題。
6. 用 3–5 分鐘展示 App 解決什麼問題、如何操作、結果是否合理。

---

## 二、最低要求與加分（重要）

本專題的底線設計是「**一週可完成**」。以下五項為**硬性最低要求**，缺一不可：

| # | 硬性要求 | 說明 |
|---|---|---|
| 1 | 可本機執行的 Streamlit App | `streamlit run app.py` 能跑，主要流程不中斷 |
| 2 | 至少一個 OpenAI API 功能 | 用 Responses API 完成明確任務 |
| 3 | **至少一項「真」結構化輸出** | Pydantic `responses.parse()` **或** `json_schema` + `strict`；**不接受純自由文字充數** |
| 4 | API key 安全 | 用 `.env` / Secrets；**不得寫死、不得上傳 GitHub** |
| 5 | GitHub repo + README | README 說明目的、安裝、執行、功能、限制 |

> ⚠️ **部署不是硬性要求。** 只到第 8 週，部署留到期末才強制；本週把部署列為加分，避免一週的時間被雲端環境排錯吃掉。

**加分項目**：

- 部署到 Streamlit Community Cloud（可公開存取網址）。
- 支援 streaming 回覆（`st.write_stream`）。
- 顯示 API 成本估算或 usage。
- 清楚的錯誤處理與輸入長度限制。
- UI 流程清楚，使用者不看程式碼也會操作。

---

## 三、建議題目（三選一或自訂）

對應課程大綱：AI 摘要器、履歷助手、客服分類器。三題覆蓋「入門 → 職涯 → 商業」難度。

| 題目 | 適合情境 | 建議輸入 | 結構化輸出範例欄位 |
|---|---|---|---|
| AI 摘要器 | 長文 / 筆記 / 會議記錄抓重點 | 一段文字或 .txt / .md | `title` / `summary` / `key_points` / `keywords` / `action_items` |
| 履歷助手 | 整理履歷並給修改建議 | 履歷文字 + 應徵職缺 | `skills` / `strengths` / `gaps` / `suggestions` |
| 客服分類器 | 分類客服訊息並給處理建議 | 客戶訊息 | `category` / `priority` / `summary` / `need_human` / `draft_reply` |

**可自訂題目**，但仍須符合第二節五項硬性要求，並於動工前完成下方「專題設計表」，經教師確認範圍。

---

## 四、專題設計表（動工前必填，取代獨立 worksheet）

先填這張表，避免「先寫畫面、後來才發現 AI 任務不清楚」。

| 欄位 | 請填寫 |
|---|---|
| App 名稱 | |
| 目標使用者 | 誰會用這個工具 |
| 使用情境 | 什麼時候需要它 |
| 使用者輸入 | 文字 / 檔案 / 表單欄位 |
| AI 要完成的任務 | 摘要 / 分類 / 改寫 / 建議 / 抽取 |
| AI 輸出格式 | 文字 / 條列 / 表格 / **結構化欄位** |
| 結構化欄位清單 | 每個欄位名稱、型態與用途 |
| 風險與限制 | 隱私 / 幻覺 / 錯誤分類 / 成本 / 輸入過長 |
| Demo 範例資料 | 展示時要用哪一筆 |

---

## 五、Starter 使用方式

本週提供 `week08_midterm_starter_claude/` 作為起點，你不需要從空白開始。

```bash
# 複製 starter → 改成自己的專題資料夾
pip install -r requirements.txt
# 複製 .env.example 為 .env 並填入 key
streamlit run app.py
```

`app.py` 待完成的 TODO：

| TODO | 你要做什麼 |
|---|---|
| `PROJECT_TITLE` / `PROJECT_DESCRIPTION` | App 名稱與一句話說明 |
| `SYSTEM_PROMPT` | AI 角色、規則與限制 |
| `ProjectResult`（Pydantic） | 你的結構化輸出欄位 |
| `build_prompt()` | 把輸入組成清楚 prompt |
| `render_project_form()` | 你的輸入表單 |
| `render_structured_result()` | 結果呈現方式 |

> starter 的結構化輸出採 **Pydantic + `responses.parse()`**（第 6 週技能）；`response.output_parsed` 會是已驗證的物件，可直接 `result.summary` 取值。

---

## 六、程式檢核清單

- [ ] `app.py` 可執行，無 syntax error。
- [ ] `requirements.txt` 完整。
- [ ] `.env` **沒有**上傳到 GitHub。
- [ ] `.gitignore` 排除 `.env`、`.streamlit/secrets.toml`、`__pycache__/`。
- [ ] 缺少 API key 時 App 顯示提示，而非崩潰。
- [ ] 輸入空白時會提醒補資料。
- [ ] 輸入長度有上限（範例為 12000 字）。
- [ ] 至少一個功能使用結構化輸出。
- [ ] README 有安裝、執行、功能、限制與 Demo 範例。

---

## 七、評分 Rubric

| 項目 | 比重 | 評分重點 |
|---|---:|---|
| 功能完整度 | 30% | App 可執行，完成一個明確任務，主要流程不中斷 |
| LLM 使用品質 | 25% | prompt 清楚、輸出穩定；**確實使用結構化輸出** |
| Streamlit UI | 20% | 表單、結果顯示、錯誤提示清楚，不看程式碼也會操作 |
| 安全與成本 | 10% | 有 `.env` / Secrets、輸入長度、成本或隱私提醒 |
| README 與 Demo | 15% | README 完整，能在 3–5 分鐘展示問題、操作與結果 |

> **安全紅線（一票否決）**：API key 寫死在程式碼或被推上 GitHub，屬重大違規，將**重大扣分**，不只是扣「安全與成本」項的幾分。

---

## 八、課堂三小時流程

| 時間 | 活動 | 產出 |
|---:|---|---|
| 50 分 | 專題規格說明、教師 demo（AI 摘要器範例）、回顧第 3–7 週技能 | 明確理解最低要求 |
| 80 分 | 選題 → 從 starter 改造 → 本機 `streamlit run` | 可本機執行的初版 App |
| 30 分 | 3–4 位快速展示、同儕回饋、集中除錯 | 修正清單 |
| 20 分 | 繳交項目、rubric、下週（文件處理）預告 | 明確繳交規格 |

---

## 九、常見問題

**Q1：一定要部署嗎？** 不用。最低要求是可本機執行的 App + GitHub repo。部署是加分，期末才強制。

**Q2：可以不用結構化輸出嗎？** 不行。本專題要求至少一項真結構化輸出（Pydantic 或 json_schema）。純自由文字不算。

**Q3：可以做聊天機器人嗎？** 可以，但必須有明確任務（如履歷修改助理、客服回覆助理），單純閒聊不易展現專題價值。

**Q4：可以直接交老師的範例摘要器嗎？** 不可以。範例只是完成度參考，你必須有自己的題目、prompt、欄位與 README。

**Q5：API key 可以放 README 或 app.py 嗎？** 不可以。只能放本機 `.env` 或 Streamlit Secrets；上傳的只能是 `.env.example` / `secrets.example.toml`。

---

## 十、繳交前最後檢查

- [ ] GitHub repo 可看到 `app.py`、`requirements.txt`、`README.md`。
- [ ] repo 內沒有 `.env`，也沒有真的 API key。
- [ ] 他人依 README 可安裝並執行。
- [ ] Demo 範例資料已備妥。
- [ ] 你能說明每個結構化欄位的用途。
- [ ] 你能說明 App 限制（隱私、AI 可能出錯、輸入過長如何處理）。
