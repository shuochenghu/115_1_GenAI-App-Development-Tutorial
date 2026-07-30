# 教材製作慣例

## 目錄與版本

- 正式教材放在 `weekNN/`。
- Notebook 原則上只保留「學生版」與「教師版」。
- 正式新產出不加 `_claude` 或 `Claude生成`；既有替代版本僅供比較。
- 第 5～7 週以 Codex「實作教材」與正式專案資料夾為主線。
- 第 8 週採「專題說明書＋學生 starter＋教師 demo」，不是 notebook pair。

## 課程主線

- 核心：Python、OpenAI Responses API、Google Colab、Streamlit。
- Gemini 與 Claude 用於跨平台比較或補充，不取代 OpenAI 主線。
- 延續既有週次的 helper 名稱、函式簽名、教學語彙與 UI 結構。
- 預設模型名稱與 API 語法可能變動；實作前以官方文件和上課帳號可用性為準。

## 教學內容

- 清楚寫出先備知識、學習目標、課堂流程、完成檢核與延伸任務。
- 先解釋心智模型，再展示最小範例，最後安排整合練習。
- 範例應包含成功、錯誤與邊界情況，尤其是輸入驗證、API 失敗、拒答、格式驗證與空輸出。
- API key 使用環境變數、Colab Secrets、`.env` 或 `st.secrets`；範例檔只提供 placeholder。
- `.gitignore` 必須排除 `.env`、實際 `secrets.toml`、`__pycache__` 等敏感或生成內容。
- 付費 API、互動式 `input()` 或可能卡住「全部執行」的流程預設關閉。

## 學生版與教師版

### 學生版

- 保留題意、函式簽名、必要 scaffold、提示與 TODO。
- 不貼入教師版完整答案。
- 下游 demo 應盡量避免因尚未完成 TODO 而產生無關的連鎖錯誤。

### 教師版

- 提供完整可讀的參考答案。
- 補上預期輸出、觀察重點、常見錯誤與講解提示。
- 不殘留真正待完成的 TODO；若文字提到 TODO，應明確是說明學生版。

## Notebook 編輯

- 用 Python `json` 模組讀寫 `.ipynb`，避免全文字串替換。
- 使用 UTF-8 與 `ensure_ascii=False`，寫入後重新解析並檢查中文。
- 保持 cell ID 唯一、cell 順序合理、執行輸出清空。
- Markdown 可使用少量 emoji、HTML 提示框與 `<font color>` 重點，但避免過度裝飾。
- code cell 註解說明「為何、何時、錯誤與安全」，不逐行翻譯語法。

## 驗證清單

### Notebook

1. 所有 `.ipynb` 可由 JSON parser 讀取。
2. cell ID 存在且不重複。
3. 普通 Python code cell 可通過 `ast.parse()`；先排除 `%`、`%%` magic 與寫入非 Python 檔案的 cell。
4. `outputs` 為空，`execution_count` 為 `null`，除非任務另有要求。
5. 無大量 `?`、`�` 或其他 mojibake。
6. 無疑似 API key、密碼或真實個資。
7. 學生版 TODO 保留且無答案洩漏；教師版答案完整。
8. 配對版本的共用章節、cell 結構與術語保持合理對齊。

### Streamlit／Python 專案

1. `.py` 通過 `python -m py_compile`。
2. `requirements.txt`、`.env.example`、`.gitignore`、README 與 secrets 範例齊全且互相一致。
3. API key 缺失時提供清楚、快速失敗的錯誤訊息。
4. 表單或按鈕避免 Streamlit rerun 重複觸發昂貴 API。
5. `st.session_state`、streaming、檔案解碼與輸入長度限制有清楚處理。
6. 能做無金鑰的 import／啟動檢查就執行；需要真實金鑰的測試必須如實標示未執行。

## 記憶同步

教材修改完成後更新 `PROJECT_MEMORY.md`：

- 新增或修改了哪些正式檔案。
- 教學設計或版本主線做了哪些決策。
- 已執行哪些靜態或實跑驗證。
- 哪些 Colab、付費 API、Streamlit 或部署測試仍待執行。

不要把臨時操作細節、重複敘述或任何秘密寫入記憶。
