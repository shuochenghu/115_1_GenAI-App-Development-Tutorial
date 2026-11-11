# AGENTS.md

本專案是 115 學年度上學期「生成式 AI 應用開發」16 週課程教材，主線使用 Python、OpenAI API、Colab 與 Streamlit。教材、教學程式註解與回覆使用繁體中文。

## 開工前

- 確認目前的儲存庫根目錄，執行 `git status --short`，保留使用者既有的修改。以當前工作區的實際路徑為準。
- 讀取 [PROJECT_MEMORY.md](PROJECT_MEMORY.md) 的近期摘要與相關決策，並用實際檔案確認目前狀態。比較 Claude 版或追查其歷史時，再查閱 [PROJECT_MEMORY_claude.md](PROJECT_MEMORY_claude.md)。
- 製作或修訂教材前，閱讀 [教材製作技能](skills/course-material-authoring/SKILL.md)、[教材製作慣例](skills/course-material-authoring/references/conventions.md)及 `PROJECT_MEMORY.md` 的「講義製作原則」。對照課綱、指定週次的現有教材與相鄰週次，確認教學目標、先備與銜接。

## 教材版本

- 正式教材預設沿用 Codex 主線。使用者指定其他版本時，依指定版本處理。既有 `_claude` 或 `Claude生成` 版本可供比較，正式新增檔案沿用主線命名。
- 首次修訂既有教材時保留原版，另存含「修訂版」的教材檔案，App 使用 `weekNN_*_revised/`。已有對應修訂版時，在該版本接續修改。單純檢視時直接讀取指定版本。
- 同步學生版、教師版及對應閱讀版。學生版保留 TODO 與提示，教師版提供完整實作、預期結果及帶課提醒。維持對應章節、執行順序與既有 Notebook 格 ID。

## 教材寫法

- 每週選一條課堂主線，替代方法放在選讀。先用熟悉情境與短例建立直覺，再連到正式名詞、資料流與程式。每格聚焦一個重點，角色分工與規格可用表格或流程圖呈現。
- 練習前交代先跑哪一格、要改哪裡、輸入與預期輸出。練習後提供具體欄位與判讀標準。核心示範可獨立執行，學生 TODO 集中在本週學習目標，未完成的函式用 `raise NotImplementedError` 明確標示。
- 程式採容易追蹤的資料流，只保留教學需要的檢查。真實 API 格沿用對應離線示範的資料格式。輸出含中文的 JSON 使用 `ensure_ascii=False`。

## API、費用與 Git

- 有明確要求時才 commit 或 push。API 金鑰使用本機 `.env`、Streamlit Community Cloud Secrets 或 Colab Secrets，保護金鑰不出現在教材、程式輸出、測試紀錄或 Git 中。
- 教材的 `RUN_*` 與 `SAVE_TEACHER_RECORD` 預設為 `False`。把 API 開關與操作放在同一格，標明先備與請求次數。沿用教材既有的請求設定，包括 SDK 的 `max_retries=0`、`timeout=60`，以及支援時的 `store=False`。
- 預設執行離線驗證，在測試程序中隔離真實的 `OPENAI_*` 環境變數。適用時使用真實 SDK 搭配 `httpx.MockTransport`。真實付費 API 呼叫須有使用者授權。

## 第 9～13 週修訂版的建置與驗證

- Notebook、閱讀版 Markdown 與 App 的生成內容從 `scripts/build_weekNN_revised.py` 修改並重建。教師導讀及 App 的 `README.md` 為手寫檔，依實際變動同步格號、格數、操作方式與驗證說明。
- 在儲存庫根目錄執行對應週次的 build 與 verify。以下以第 10 週為例。

  ```powershell
  .\.venv\Scripts\python.exe -X utf8 scripts/build_week10_revised.py
  .\.venv\Scripts\python.exe -X utf8 scripts/verify_week10_revised.py
  ```

- Notebook 與 App 共用函式維持相同的 AST，由 verify 檢查。修改第 9～13 週共用的生成模組後，重建並驗證受影響的五週。
- 程式格開頭沿用 `# 用途：…；先備：…；N次API`。跨格名稱與來源由 `scripts/notebook_cell_notes.py` 產生。新增程式格時，在該週的 `CELL_NOUNS` 補上名稱。主節標題使用 `## 2 標題` 的格式，讓 Colab 目錄顯示節次。

## 交付

- 修改 Notebook 後檢查 JSON、唯一格 ID、程式格語法、執行順序、亂碼及學生 TODO。確認教師版答案、閱讀版與生成來源同步。
- 教材變更後更新 `PROJECT_MEMORY.md`，記錄產物、決策、驗證結果與待驗證事項。若涉及 Claude 版或需更新其鏡像內容，再同步 `PROJECT_MEMORY_claude.md`。
- 依實際執行結果回報靜態檢查、離線測試與真實 API 呼叫次數。若任務涉及 Colab、Cloud 部署、真人瀏覽器或試教，註明各項驗證狀態。
