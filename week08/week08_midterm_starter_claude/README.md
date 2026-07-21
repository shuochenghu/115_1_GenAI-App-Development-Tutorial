# 期中個人小專題 Starter（Claude 版）

> 這是第 8 週期中專題的**起始骨架**，可直接執行、再依 TODO 改造成你的題目。
> 對應教材：`生成式AI應用開發_第08週_期中個人小專題_專題說明書_Claude生成.md`

---

## 這個 starter 提供什麼

- 一個可執行的 Streamlit App（`app.py`），內含：
  - 對齊第 7 週的 helper：`get_secret()` / `create_client()` / `ask_ai()` / `stream_ai()`
  - 第 6 週的結構化輸出（Pydantic）：`extract_structured()` + `ProjectResult`
  - 輸入驗證、API key 缺失提示、錯誤處理、輸入長度上限
- 秘密檔範本：`.env.example`、`.streamlit/secrets.example.toml`
- 已設定好的 `.gitignore`（排除 `.env`、`secrets.toml`、`__pycache__/`）

---

## 快速開始

```bash
# 1) 安裝套件
pip install -r requirements.txt

# 2) 建立本機 .env（複製範本後填入你的 key）
#    Windows PowerShell:  Copy-Item .env.example .env
#    macOS / Linux:       cp .env.example .env

# 3) 執行
streamlit run app.py
```

> 尚未填 `OPENAI_API_KEY` 也能開啟畫面，App 會顯示提醒；填好 key 後即可實際呼叫 API。

---

## 你要完成的 TODO

| 位置 | 你要做什麼 |
|---|---|
| `PROJECT_TITLE` | App 名稱 |
| `PROJECT_DESCRIPTION` | 一句話說明解決什麼問題 |
| `SYSTEM_PROMPT` | AI 的角色、規則與限制 |
| `ProjectResult` | 結構化輸出的欄位（改成你的題目需要的欄位） |
| `build_prompt()` | 把使用者輸入組成清楚的 prompt |
| `render_project_form()` | 你的輸入表單欄位 |
| `render_structured_result()` | 結果要怎麼呈現給使用者 |

---

## 繳交前檢查（對應說明書 rubric）

- [ ] `app.py` 可執行，無 syntax error。
- [ ] `.env` **沒有**被上傳到 GitHub（只上傳 `.env.example`）。
- [ ] 缺少 API key 時 App 會提示，而不是崩潰。
- [ ] 至少一個功能使用結構化輸出。
- [ ] README 說明安裝、執行、功能、限制與 Demo 範例。

> 安全紅線：API key 只能放 `.env` 或 Streamlit Secrets，**寫死或推上 GitHub 會被重大扣分**。

---

## 環境變數

| 變數 | 用途 | 預設 |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI 金鑰 | 無（必填） |
| `OPENAI_MODEL` | 使用的模型 | `gpt-5.4-mini` |
