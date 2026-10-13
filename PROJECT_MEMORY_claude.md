# 專案工作記憶（Claude 版）

此檔用來保存可隨專案移動的工作狀態，方便在不同電腦或不同 AI 工具中接續處理。請勿在此檔寫入 API key、密碼、信用卡、學生個資或其他機密資料。

## 與 Codex 記憶的關係（2026-10-13 同步）

- **`PROJECT_MEMORY.md`（Codex 維護）是專案現況的權威來源**；本檔與其同步現況、講義製作原則與待辦，另外保存 Claude Code 產出的替代版本（`_claude`／`Claude生成`）紀錄。兩檔衝突時以 `PROJECT_MEMORY.md` 與實際檔案為準，並回頭修正本檔。
- 本次同步基準：分支 `Home_Test`、提交 `842f212`（Update PROJECT_MEMORY.md），已核對 `week01/`～`week12/` 實際檔案、`skills/course-material-authoring/` 與各週修訂／比較紀錄。
- Claude Code 開始工作時：先讀 `PROJECT_MEMORY.md`（尤其「公司電腦接續摘要」「講義製作原則」），再讀本檔的 Claude 版紀錄；修改教材後兩檔都要更新，避免再次落差。
- 教材製作 skill：`skills/course-material-authoring/SKILL.md` 與 `references/conventions.md`（Codex 建立，Claude 製作教材時同樣遵守）。

## 目前接續摘要（2026-10-13，同步自 Codex「公司電腦接續摘要」）

若較舊紀錄提到第 5、6 週語音銜接，以 10 月 13 日「已刪除」為現行決策。

### 工作區

- 家裡專案位置 `K:\115_1_GenAI-App-Development-Tutorial`；本機（另一台電腦）為 `E:\Git Repos\115_1_GenAI-App-Development-Tutorial`。以實際專案位置為準，不沿用其他電腦的絕對路徑或 Python 環境。
- 換電腦接續前先確認 Git 狀態與遠端是否含最新提交，不能只靠聊天歷史。

### 現行修訂版本（後續在這些檔案續改，不另建重複修訂版）

| 週次 | 現行版本 | 現況 |
|---|---|---|
| 第 1 週 | `week01/生成式AI應用開發_第01週教材_語音增補修訂版.md`、`生成式AI應用開發_第01週投影片_語音增補修訂版.md`／`.html` | 23 頁；STT→確認文字→文字回答→TTS 概念、10 分鐘預錄示範腳本與設備調查。評量 40／20／25／10／5%，期末至少 RAG 或 Function Calling。原始三檔保留，尚未製作實際音檔。 |
| 第 4 週 | `week04/..._Prompt_Engineering實作教材_150分鐘修訂版_學生版／教師版.ipynb` | 各 72 cells（43 Markdown、29 code）；G、A 必做，B/C 擇一，v3 延伸。詳見 `week04/第04週_150分鐘修訂版_修訂與驗證紀錄.md`。 |
| 第 5 週 | `week05/..._對話狀態_Streaming與聊天機器人實作教材_150分鐘修訂版_學生版／教師版.ipynb` | 各 63 cells；%pip、Secrets 與重啟順序、套件版本顯示、`max_retries=0`、可調 60 秒 timeout；已刪除語音預告；固定活動規劃 15 次請求。 |
| 第 6 週 | `week06/..._Structured_Outputs_JSON_Schema與資料抽取實作教材_150分鐘修訂版_學生版／教師版.ipynb` | 各 70 cells；JSON Schema 先教，G 與 A 必做、B/C 擇一，主線 7 次請求、選讀另 1 次；事件欄位驗證、A2 六項離線契約、Colab 提示與 60 秒 timeout；已刪除語音預告。 |

第 4～6 週原始版與 Claude 參考版保留。學生 TODO 與教師答案分工、ID、順序、付費旗標預設 False 均保留。

### 使用者已確認的教學取捨

- 第 5、6 週沒有語音 API 範例或練習，不得只因「未來可以整合」就加入 STT／TTS 預告；更新與重建腳本也不會加回。
- 第 6 週 Schema 版本管理、巢狀會議模型、重試 R 保留為課後延伸；第 7／8 週 App 銜接保留。
- 語音概念保留在第 1 週；第 12 週增補語音輸入與輸出是後續規劃，目前第 12 週仍是 Vision 教材與 App，尚未修改第 12 週、主課綱或第 7 週 App。
- 60 秒是待課前實測的網路等待起始值，不是串流總時間上限；套件版本顯示供紀錄，Colab 驗證後再固定安裝版本，不可直接套用 Windows 完整快照。

### 腳本入口（Codex 建立）

- `scripts/update_colab_runtime_guidance.py`（第 5、6 週更新）、`scripts/verify_colab_runtime_guidance.py`（共同離線驗證）。
- `scripts/build_week06_revision.py`、`scripts/verify_week06_revision.py`（第 6 週重建／檢查）；`scripts/build_week01_voice_revision.py`（第 1 週來源）。
- `scripts/verify_classroom_environment.py`（第 7–12 週 App 課堂環境離線檢核）。
- 上述第 5、6 週檢查以假 OpenAI 模組替代 SDK；未執行真實 API、Colab 或 150 分鐘試教，不得把離線通過寫成真實驗證成功。

### 下一步

下一個要修改的週次尚未指定。候選：「第 12 週語音實作及主課綱同步規劃」或「第 5、6 週 Colab 課前實測」；不把規劃視為已完成或自動開始。

## 專案定位

本資料夾是 115 學年度上學期課程大綱與教材工作區，主要正在製作「生成式AI應用開發」課程教材。課程主線以 Python、OpenAI API、Google Colab、Streamlit 為核心；Claude API 與 Gemini API 作為比較或補充版本，不作為主要教學主線。

## 講義製作原則（2026-10-06 確認，後續製作與修訂必須沿用；與 `PROJECT_MEMORY.md` 同文）

適用本專案各週Notebook、實作講義與學生／教師教材。開始工作時先讀本節，規劃與交付前逐項核對；使用者當次明確指示優先。第四、第五周150分鐘修訂版為本次做法的參考，應依各週目標調整，不機械複製題型或cell數量。

1. **先確認課程銜接與時間安排。** 檢視前周先備、本周目標、後續應用與實際教材；150分鐘包含講解、示範、實作、除錯與討論，明確區分必做、擇一、選讀與延伸，不把所有內容列為必做。
2. **依理解與操作順序編排。** 採「概念→完整示範→引導練習→學生實作→結果檢查→反思」；新概念先解釋再使用，練習緊接相關主題。完整示範不依賴學生尚未完成的TODO；若有依賴，須明確標示先備及可用替代示範。
3. **文字cell與code cell緊密對應。** 程式前交代目的、輸入、回傳值、資料流與責任；程式後交代預期結果、判讀與常見錯誤。長程式依責任拆格，維持清楚的定義與執行順序，不為湊數增加cells。
4. **語法／細節選讀必須連回正式程式。** 新增或修訂教材時主動盤點兩版所有code cells中的非基礎Python語法，先對照前週實際教材確認已教內容；只有本週新出現、對完成核心任務有必要且難以從簡短註解理解的語法才新增選讀，不等使用者逐一指出。已教語法以一兩句用途提示或前週回查處理，基礎語法不另加長選讀；共用語法集中解釋，避免每種語法都變成獨立選讀或小示範。指明對應函式、變數與原程式片段，提供「離線小示範→正式程式」對照、逐步讀法、預期觀察與限制；讀完能回到指定code cell理解用途。不要只孤立介紹Python語法，也不要用選讀示範揭露整題學生答案。
5. **程式註解解釋目的與原因。** 使用繁體中文，說明區塊責任、API與資料流、函式傳入／執行時機、狀態更新與錯誤處理。語法選讀配套code cells也必須有註解，標明正式程式的對應位置；避免只翻譯明顯語法或只在文字cell解釋。
6. **每項TODO都有具體規格。** 列出情境、已提供內容、學生負責項目、輸入型別、回傳值、結果保存變數、執行順序與完成條件；編號與說明逐項對應。指出哪些helper、資料及固定測試器不需修改。區分return、print、回傳物件與副作用，避免學生只顯示結果卻未保存。
7. **學生版與教師版同步製作。** 同章節、活動、程式責任及執行順序；學生版保留必要骨架、提示與TODO，教師版提供完整實作、預期結果及判讀標準。共用helper與固定測試器直接提供，練習集中在本周學習目標；未完成處明確提示，不以空值冒充完成。
8. **實驗與檢查條件明確。** 比較時固定資料與規則，指出操弄因素，測試題不混入few-shot範例。區分格式／標籤合法、答案正確、契約錯誤與API／回應失敗；不預設few-shot一定改善，也不以偶然回答證明記憶或reset。說清楚程式檢查、人工核對與測試限制。
9. **執行開關放在使用位置。** 真實API旗標與對應if操作放在同一code cell，預設False；同格標示先備、開啟方式與請求數。不同活動可獨立開啟與重跑，避免集中在環境cell宣告。互動CLI預設不啟動，先提供離線示範與檢查；新增解說不應無故增加付費呼叫。
10. **驗證、繳交與紀錄一致。** 列明交件、實際input／輸出、測試證據與反思；交付前檢查JSON、唯一ID、輸出、語法、執行順序、版本分工及必要的成功／失敗行為。區分靜態、離線、真實API、Colab與試教，未執行項目明確標記；假回應不能充當真實成果。保留原始教材，首次修訂另存，後續在使用者指定修訂版繼續修改；同步修訂紀錄及本專案記憶，不自動改動其他週次。

後續交付自查：學生是否知道改哪裡、傳入什麼、回傳／保存什麼、依序執行哪格、如何證明完成？選讀是否指出正式程式位置？API開關是否緊鄰活動？教師答案與學生規格是否一致？

## 版本主線與命名規則（重要）

- **正式主線一律為 Codex 版**（skill 規定「Prefer the formal Codex track unless the user explicitly names another variant」）；最早於 2026-07-21 確立第 5–7 週，之後第 8–12 週沿用。Claude 版為比較／備援，不是預設對齊對象。
- 新教材延續時，以 Codex 版的檔案結構、helper 命名、函式簽名為基準。課堂第 7 週使用 `week07/week07_streamlit_app/`，helper：`get_secret()`、`create_client()`、`ask_ai(user_input, system_prompt=...)`、`stream_ai(...)`。`extract_structured()` 源自第 6 週結構化輸出。
- 檔名：`..._Claude生成.ipynb`、`*_claude/`、`..._Claude生成.md` ＝ Claude Code 產出；`...實作教材_....ipynb` ＝ Codex 產出；`..._150分鐘修訂版_...`／`..._語音增補修訂版...` ＝ 在 Codex 正式版上的修訂版（目前的續改對象）。
- 正式課程 starter／範例專案（如 `week08_midterm_starter/`）與 Codex 新產出不加工具後綴；`_claude`／`Claude生成` 只保留給既有 Claude 參考檔，正式新產出不使用。
- 所有教材位於 `week01/`～`week12/` 週資料夾（2026-07-21 重整），引用請用 `weekNN/...` 路徑。
- 專案中沒有 repo 層 `CLAUDE.md`；Claude Code 的入口是本檔與 auto-memory。Codex 另有 `.codex/config.toml`（`workspace-write`、`approval_policy = "never"`）。

## 目前教材狀態

課程主大綱：`生成式AI應用開發_16周課程大綱.md`（實際 18 週，含 16 週授課與第 17、18 週自主學習）。Notebook 只保留「學生版」與「教師版」。

### 第 1 週（`week01/`）
- 原始：`生成式AI應用開發_第01週教材.md`、`生成式AI應用開發_第01週投影片.md`／`.html`（21 頁）。
- **現行**：語音增補修訂版三檔（23 頁 Marp），紀錄 `第01週_語音增補修訂與Colab檢視紀錄.md`。

### 第 2 週（`week02/`）
- `..._第02週_Python複習_學生版／教師版.ipynb`：各 63 cells；含 with／context manager、type hints 快速讀法、「3-3 用函式指定排序規則與 lambda」。教師版保留 18 個既有已執行／含輸出 cells。

### 第 3 週（`week03/`）
- OpenAI／Gemini／Claude API 入門學生版／教師版（OpenAI 為主線；Gemini 各 33 cells）。
- `生成式AI應用開發_第03週投影片.md`（25 頁 Marp，OpenAI 主線，不提第 4 週）與 `.pdf`。

### 第 4 週（`week04/`）
- Codex：`..._Prompt_Engineering實作教材_學生版／教師版.ipynb`（40 cells）、`..._實作教材_修訂版_...`、**`..._實作教材_150分鐘修訂版_...`（現行，72 cells）**，紀錄 `第04週_150分鐘修訂版_修訂與驗證紀錄.md`。
- Claude：`..._Prompt_Engineering_學生版／教師版_Claude生成.ipynb`（35 cells）。

### 第 5 週（`week05/`）
- Codex：`..._對話狀態_Streaming與聊天機器人實作教材_學生版／教師版.ipynb`（現為 42 cells）、**`..._150分鐘修訂版_...`（現行，63 cells）**，紀錄 `第05週_150分鐘修訂版_修訂與驗證紀錄.md`。
- Claude：`..._對話與Streaming_學生版／教師版_Claude生成.ipynb`（33 cells）。

### 第 6 週（`week06/`）
- Codex：`..._Structured_Outputs_JSON_Schema與資料抽取實作教材_學生版／教師版.ipynb`（40 cells）、**`..._150分鐘修訂版_...`（現行，70 cells）**，紀錄 `第06週_150分鐘修訂版_修訂與驗證紀錄.md`。
- Claude：`..._Structured_Outputs與資料抽取_學生版／教師版_Claude生成.ipynb`（31 cells）。

### 第 7 週（`week07/`）
- Codex（正式）：`..._Streamlit_Web_App入門實作教材_學生版／教師版.ipynb`（各 40 cells）＋ `week07_streamlit_app/`。
- Claude：`..._Streamlit_Web_App入門_學生版／教師版_Claude生成.ipynb`（40 cells）＋ `week07_streamlit_app_claude/`。
- `生成式AI應用開發_第07週_Git實作教材.md`：GitHub Desktop／GitHub／Community Cloud 部署補充講義。

### 第 8 週（`week08/`，期中個人小專題）
- 規劃：`..._第08週_期中個人小專題_內容規劃.md`（七項決策定案）。
- Codex（正式）：`..._專題說明書.md`、`week08_midterm_starter/`、`week08_midterm_example_summarizer/`（JSON Schema + `strict`）。
- Claude：`..._專題說明書_Claude生成.md`、`week08_midterm_starter_claude/`、`week08_midterm_example_summarizer_claude/`（Pydantic `responses.parse()` + `output_parsed`）。

### 第 9 週（`week09/`）
- Codex（正式）：`..._文件處理與資料前處理實作教材_學生版／教師版.ipynb`（各 36 cells）＋ `week09_document_processor/`。
- Claude：`..._文件處理與資料前處理_學生版／教師版_Claude生成.ipynb`（36 cells）＋ `week09_document_processor_claude/`。
- 比較：`..._第09週_文件處理_Claude與Codex版比較.md`。

### 第 10 週（`week10/`）
- Codex（正式，**已產出**）：`..._Embedding與語意搜尋實作教材_學生版／教師版.ipynb`（各 34 cells）＋ `week10_semantic_search_app/`（`requirements-chroma.txt` 為 ChromaDB 選讀安裝入口）。
- Claude：`..._Embedding與語意搜尋_學生版／教師版_Claude生成.ipynb`（31 cells）＋ `week10_semantic_search_claude/`。
- 比較：`..._第10週_Embedding與語意搜尋_Claude與Codex版比較.md`（2026-08-04）。

### 第 11 週（`week11/`）
- Codex（正式）：`..._RAG基礎與文件問答實作教材_學生版／教師版.ipynb`（各 40 cells）＋ `week11_rag_app/`。
- Claude：`..._RAG基礎與改良_學生版／教師版_Claude生成.ipynb`（32 cells）＋ `week11_rag_qa_claude/`。
- 比較：`..._第11週_RAG_Claude與Codex版比較.md`。

### 第 12 週（`week12/`，已於 2026-09-18 提交 `ed000e8`）
- Codex（正式）：`..._多模態應用_Vision_API與圖片理解實作教材_學生版／教師版.ipynb`（各 40 cells）＋ `week12_vision_app/`。
- Claude：`..._Vision_API與圖片理解_學生版／教師版_Claude生成.ipynb`（40 cells）＋ `week12_vision_app_claude/`。
- 比較：`..._第12週_Vision_Claude與Codex版比較.md`。`sample_data/*.png` 未納入版控（由 `create_demo_receipt.py` 產生）。

### 共用
- `docs/課堂環境與部署指南.md`、`environments/classroom-windows-py312.txt`、`scripts/`（見上方腳本入口）、`skills/course-material-authoring/`。

## 已完成的重要決策（各週主線，同步自 Codex）

- **第 1 週**：API 費用由學生自行負擔，課程不提供免費額度；教師開課前依預計呼叫、token 與當時官方價格公告預估與建議上限，作業與專題另訂上限；區分消費提醒與硬性上限。課綱第十八節同步，移除固定新台幣估算。
- **第 2 週**：API 開發前的 Python 快速複習（函式、f-string、list／dict、type hints、with、lambda／sorted key、JSON、例外處理、API key 管理、公開 API 呼叫）；with 只講入門心智模型；第六節含 Colab Secrets、PowerShell、`setx`、`export` 等金鑰設定方式。
- **第 3 週**：OpenAI Responses API（`client.responses.create()`、`response.output_text`、`previous_response_id`）；預設模型 `gpt-5.4-mini`。Gemini 用 `google-genai`、`client.interactions.create()`、`previous_interaction_id`（2026-09-15 補明 `system_instruction` 每輪重送、`store=false` 不能用前次 ID）；Claude 用 `client.messages.create()` 並送完整 history。練習 A 批改助教、B usage 與費用、C 自訂角色。
- **第 4 週**：OpenAI 主線；system prompt、任務拆解、格式控制、few-shot、`compare_prompts()`，四大功能 summarize／classify／rewrite／answer_question（只依參考資料回答，為第 11 週 RAG 雛形）。150 分鐘修訂版見上表。
- **第 5 週**：獨立請求、`previous_response_id`、手動 history、有限視窗、重要事實記憶、usage、reset、Streaming（處理 `response.output_text.delta`、`response.completed`、`error`；完成事件後才更新 ID 與 transcript）；`run_console_chat()` 預設註解。
- **第 6 週**：JSON Schema first（`text.format` + `json_schema` + `strict` + `json.loads()`），Pydantic `responses.parse()` 為補充，不採 Claude 版 Pydantic-first；helper 含 refusal／空輸出檢查；保留三層讀法等可讀性橋接。
- **第 7 週**：Streamlit Web App 入門（非 Git）；notebook 講解 + VS Code 專案；聊天採手動有限 history（最近五輪、每輪重送 instructions），只在完成且非空時保存訊息配對，串流辨識 completed／error／failed／incomplete（2026-09-15 修正）。
- **第 8 週**：說明書 + starter + 教師 demo；七項決策（2026-07-21）：①對齊 Codex 第 7 週；②Claude 產出加 `_claude`；③部署只加分、期末才強制；④結構化輸出為硬性最低要求；⑤三題目＋開放自訂；⑥rubric 30/25/20/10/15、API key 外洩一票否決；⑦專題設計表內嵌說明書。2026-09-15 兩個 Codex `app.py` 補 refusal → incomplete（區分長度限制／內容過濾）→ 其他非完成狀態 → 空輸出／`json.loads()` 的失敗分流。
- **第 9 週**：六層管線（輸入→格式路由→抽取→清理→chunking→應用），本機確定性處理、AI 摘要按鈕觸發；字元滑動視窗 + overlap 為基礎，段落優先切割為必做練習；先複習 type hints；上傳上限 8 MB（`.streamlit/config.toml`）。
- **第 10 週**：Codex 正式主線為 `list[dict]` + NumPy + cosine 的最小索引，OpenAI Embeddings 為主動開啟的付費模式；ChromaDB 只作 preview／選讀、FAISS 只作概念比較，皆非必要依賴（Claude 版為 ChromaDB-first 參考）。
- **第 11 週**：ChromaDB 為必要向量庫（`EphemeralClient()`），教 Retrieval、context、來源引用、證據不足拒答、基本評估；索引與生成是兩個明確操作；文件內容視為不可信任資料。2026-08-11 加入 `evaluate_retrieval()`（檢索層）與 `evaluate_rag_answer()`（生成層）區分。FAISS、持久化、hybrid、reranking 留進階。
- **第 10、11 週 ChromaDB 設定（2026-09-15）**：Codex 正式版改用 `configuration={"hnsw": {"space": "cosine"}}`，來源存於 `metadatas`；Claude 參考版未改（見「Claude 版與 Codex 已知差異」）。
- **第 12 週**：Responses API `input_image` + Base64 data URL；本機 signature + Pillow 驗證格式、尺寸、像素、非動態 GIF，8 MB 上限；表單按鈕觸發 API；收據／表單沿用 JSON Schema strict；detail 只提供 `auto`／`low`／`high`；`store=False` 不代表圖片未傳送；所有文字數字需人工回看原圖。

## 課堂環境（2026-09-16，Codex 建立）

- 第 7–12 週正式 App 的 requirements 固定直接依賴，基準 Windows x86_64／Python 3.12.13、Streamlit 1.63.0、OpenAI SDK 2.49.0、python-dotenv 1.2.3、NumPy 2.5.3、pandas 3.0.5、pypdf 6.18.1、python-docx 1.2.0、ChromaDB 1.5.9。
- 完整快照 `environments/classroom-windows-py312.txt`，不可直接當 Linux 雲端 lock。Streamlit 1.46 起支援入口程式旁的 `.streamlit/config.toml`，從 repo 根目錄或 App 目錄啟動皆可載入。
- 第 12 週在現有 Windows／Python 3.14 `.venv` 實跑；課堂 Python 3.12 乾淨環境尚未對第 12 週建立。
- Claude 版專案的 requirements 未依此固定（僅 Codex 正式版同步）。

## Claude 版專屬紀錄

### 第 3 週投影片
- `week03/生成式AI應用開發_第03週投影片.md`：25 頁 Marp，Claude 產出；內文移除第 4 週前向指涉，擴充 Gemini／Claude API 差異（對照表、程式寫法、多輪對話、選用建議）。

### 第 4～6 週 Claude 版
- 第 4 週：35 cells，四大功能與課堂練習（A 會議記錄、B few-shot 垃圾郵件、C 選做 prompt 測試）保留 TODO。
- 第 5 週：33 cells，方法 A／B 比較、`ChatSession`（`_trim()`、`reset()`）、`stream_reply`、`chat_bot()`（教師版預設註解）；練習 A 英文練習夥伴、B `max_turns=1` 遺忘、C 累計 token。2026-07-14 比較結論：Claude 版需補 API 失敗不污染 history、空白輸入驗證、Streaming 接上 history；正式主線已定為 Codex 版，這三項修正僅在需要備援版時套用。
- 第 6 週：31 cells，Pydantic-first；練習 A `ResumeInfo`、B 巢狀 `OrderInfo`、C `extract_with_retry()`；demo cell 用 `print(model)` 避免學生未完成 TODO 時連鎖錯誤。其優點（欄位驗證表、`MeetingMinutes`、`extract_structured()`、refusal 提醒）已被 Codex 正式版吸收。

### 第 7 週 Claude 版
- `%%writefile` 漸進產生 `app_1_hello.py`→`app_4_chat.py`，含 Colab localtunnel 備援；secrets 雙軌 `.env` + `st.secrets`（`get_secret()`）；練習 A 側邊欄 system prompt、B 翻譯／分類表單、C 累計成本。`week07_streamlit_app_claude/` 通過 `py_compile`，付費 API／實跑未執行。

### 第 8 週 Claude 版
- 說明書反映七項定案；兩專案 helper 對齊 Codex 第 7 週（`get_secret`／`create_client`／`ask_ai`／`stream_ai`），結構化輸出改用 Pydantic；Codex 正式版已吸收其「真 structured output」要求、安全紅線、optional `stream_ai()`、檔案上傳與串流摘要示範。

### 第 9 週 Claude 版（2026-07-31）
- helper 對齊 Codex：`decode_text_bytes`（utf-8-sig/utf-8/cp950）、`extract_pdf_text`（`[第 N 頁]`）、`extract_docx_text`、`extract_csv_text`（限 200 列）、`extract_text`、`clean_text`、`chunk_text`、`get_secret`、`summarize_document`。
- 學生版 6 TODO（`clean_text`／`chunk_text`／`summarize_document` + A `chunk_by_paragraph`／B `build_document_report`／C `challenge_plan`），graceful degradation；`RUN_PAID_API=False` 守門。教師版本機程式實跑通過。

### 第 10 週 Claude 版（2026-08-04）
- helper：`get_embedding(text, offline=)`、`embed_texts`、`cosine_similarity`、`search_chunks`、`build_chroma_collection`、`query_chroma`；ChromaDB-first（Codex 正式版改為 NumPy-first）。
- 差異化：離線假 embedding `local_demo_embed()`（字元 + bigram + 空白斷詞雜湊），明確標註「非真語意」；Codex 正式版已吸收此概念。
- 學生版 6 TODO（`cosine_similarity`、`get_embedding` 真 API 分支、`search_chunks`、A `build_chroma_collection`、B `query_chroma`、C `challenge_plan`）。

### 第 11 週 Claude 版（2026-08-11）
- helper 依使用者裁示 (a) 對齊 Codex `rag_utils`：`build_rag_context`(→str)／`build_rag_prompt`／`generate_rag_answer`／`format_sources`(→list)／`evaluate_rag_answer`／`answer_from_hits`，常數 `DEFAULT_GENERATION_MODEL`／`INSUFFICIENT_EVIDENCE_MESSAGE`；hits 為扁平結構。
- TODO：核心 `build_rag_context`／`answer_from_hits`（graceful）+ 練習 A `evaluate_retrieval`／B `filter_hits_by_score`（`NotImplementedError`）／C `challenge_plan`。
- 品質修正（2026-08-11）：第 9–11 週 notebook `cell_type` 由 `"md"` 改 `"markdown"`；學生版 `run_local_checks()` 改為註解；`app.py` 索引簽章用 `hashlib.sha256(file_bytes)`；按「建立／更新索引」按鈕才建索引；README 更新。`build_rag_context` 只對實際保留的非空片段連續編號。

### 第 12 週 Claude 版（2026-09-16）
- helper 一開始即對齊 Codex `vision_utils.py`：`detect_image_mime`／`validate_image`／`image_to_data_url`／`build_task_prompt(mode, question)`／`get_refusal_reason`／`require_completed_response`／`analyze_image(file_bytes, *, mode, question, detail, model)`／`RECEIPT_SCHEMA`／`get_secret`／`create_client`；Notebook 的 given helper 由 builder 以 `inspect.getsource` 從專案取出。
- 學生版 6 TODO（核心 `validate_image`／`build_task_prompt` graceful + A `choose_detail`／B `normalize_receipt`／C `evaluate_vision_answer` 用 `NotImplementedError` + D `challenge_plan`）。
- 差異化：離線示範模式 `analyze_image(..., offline=True)`（`OFFLINE_DEMO_NOTICE`）、`build_request`／`preview_request`、模糊旋轉收據、練習 helper 放進專案、Claude API 圖片輸入對照表（選讀）。
- 驗證：兩版全部 code cell 離線依序執行 0 錯誤、3 個 .py `py_compile`、`vision_utils` 煙霧測試、Streamlit `AppTest`。**本機已設定 `OPENAI_API_KEY`，曾意外真實呼叫一次 `analyze_image`；之後測試一律清空金鑰。**

### Claude 版與 Codex 已知差異（未同步，僅記錄）
- 第 10、11 週 Claude 版 `embedding_utils.py:183` 仍用 `create_collection(name, metadata={"hnsw:space": "cosine"})`；Codex 正式版已改 `configuration={"hnsw": {"space": "cosine"}}`。
- 第 11 週 Claude 版 embedding 層函式名保留 `build_chroma_collection`／`query_chroma`，未改成 Codex 的 `build_chroma_index`／`query_chroma_index`（刻意維持與第 10 週 Claude 版一致）。
- 第 12 週 Codex 版 Notebook 與專案函式名不一致（`validate_upload`／`analyze_image_bytes`／`extract_receipt` vs `validate_image`／`analyze_image`）；比較文件建議 Codex 統一並吸收模糊測試圖、練習 helper 放進專案。
- Claude 版各週 App requirements 未固定版本、未納入 `scripts/verify_classroom_environment.py`。
- 第 2、5、10 週 Codex 正式版的 2026-09-22 lambda／callback／sorted 補強、第 7 週 history 修正、第 8 週失敗分流等，均未回補至 Claude 版。

## 編輯與驗證原則（同步 Codex 現行規則）

- 修改 notebook 時用 Python `json` 模組讀寫 `.ipynb`，不用全文字串替換。
- **輸出 notebook 使用 `json.dumps(..., ensure_ascii=False, indent=1)`**，保留可讀繁體中文；寫入後必須重新解析 JSON 並檢查亂碼（取代早期為避免 Colab／Windows 中文變 `?` 而使用的 `ensure_ascii=True`）。
- 修改學生版時保留 TODO，不貼回教師版答案；教師版可保留完整答案與示範程式，不殘留真正待完成的 TODO。
- 生成或修改程式碼時加入繁體中文教學型註解與結構化 docstring（目的、參數、回傳、可能錯誤、教學重點）；避免逐行翻譯明顯語法。
- Markdown 可用少量 emoji、HTML 提示框與 `<font color="..."><b>…</b></font>`（Colab 對 CSS `style` 支援不穩），避免過度裝飾；callout 只放安全／成本／幻覺等紅線。
- 每次生成或修改某一週教材後，同步更新 `PROJECT_MEMORY.md` 與本檔的教材狀態、進度、決策與下一步，並保留原始教材、不自動改動其他週次。
- 每次修改 notebook 後至少檢查：
  - JSON 可解析；每個 cell 的 `cell_type` 只能是 `"markdown"` 或 `"code"`（曾因 builder 寫成 `"md"` 導致第 9–11 週 Claude notebook 失效）。
  - cell ID 存在且唯一；`outputs` 清空、`execution_count` 為 `null`（另有要求除外）。
  - 普通 Python code cell 通過 `ast.parse()`（排除 magic 與寫入非 Python 檔的 cell），無 SyntaxWarning。
  - 無大量 `?`、`�` 等亂碼；無疑似 API key 或個資。
  - 學生版主要練習保留 TODO 且無答案洩漏；學生版「Run All」不中斷（`run_local_checks()` 等自我檢查要註解並附說明）。
- Streamlit 專案：`.py` 通過 `py_compile`；requirements／`.env.example`／`.gitignore`／README／secrets 範例一致；表單或按鈕避免 rerun 重複觸發付費 API；無金鑰能做的 import／啟動檢查就執行，真實金鑰測試未執行要如實標示。
- 本機有真實 `OPENAI_API_KEY`：離線測試前先清空該環境變數。

## 模型與環境變數

- OpenAI 預設模型：`gpt-5.4-mini`（`OPENAI_MODEL` 可覆蓋）；Embeddings：`text-embedding-3-small`。
- Gemini 預設模型：`gemini-3.5-flash`（`GEMINI_MODEL`）。
- Claude 預設模型：`claude-haiku-4-5`（`CLAUDE_MODEL`）。
- 若任一預設模型在上課帳號不可用，課前改成實際可用模型。

## 最近工作進度（新→舊，同步自 Codex；細節見 `PROJECT_MEMORY.md` 與各週紀錄）

- 2026-10-13：Claude 依使用者要求同步本檔與 auto-memory 至 Codex 記憶（`842f212`）；第 12 週比較文件更新提交狀態。未改動任何教材內容。
- 2026-10-13：Codex 於 `PROJECT_MEMORY.md` 開頭建立「公司電腦接續摘要」；依使用者指示移除第 5、6 週 150 分鐘雙版的語音銜接預告（code cells 完全不變，各只改一格 Markdown），並移除學生教材中的修訂作業說明。
- 2026-10-12：第 5、6 週 150 分鐘雙版補 Colab 操作、`API_TIMEOUT_SECONDS=60.0`、SDK 版本顯示、Secrets 授權與 runtime 重啟順序；第 5 週 `max_retries=0` 與 `%pip`。第 1 週另存語音增補修訂版（21→23 頁）。第 6 週 150 分鐘修訂版建立（64 cells）後再改善為 70 cells。
- 2026-10-06：確認「講義製作原則」；第 4 週 150 分鐘修訂版 72 cells；第 5 週經全面展開語法（75 cells）後依第 4 週精簡為 63 cells。
- 2026-09-22：第 2 週補 lambda 先備（各 63 cells）；第 5 週補 callback 建立／呼叫時機；第 10 週補 sort／sorted 與 top-k 排序複習。
- 2026-09-16：Codex 與 Claude 各自完成第 12 週；Codex 固定課堂環境並建立部署指南與檢核腳本（2026-09-18 提交）。
- 2026-09-15：第 1 週 API 費用政策與課綱第十八節；第 3 週 Gemini 多輪說明；第 7 週聊天 history／串流完成事件修正；第 8 週 Structured Outputs 失敗分流；第 10、11 週 ChromaDB `configuration` 寫法。
- 2026-08-11：Codex 完成第 11 週並補 `evaluate_retrieval()`；Claude 完成第 11 週並對齊 Codex `rag_utils`，修正第 9–11 週 `cell_type` 與 Run All 中斷。
- 2026-08-04／08-05：Codex 完成第 10 週並寫比較文件；第 9 週註解繁中化、吸收 Claude callout；第 2、9 週補 type hints。Claude 完成第 10 週。
- 2026-07-28～07-31：第 2 週 with 橋接；第 7、8 週程式註解補強；第 8 週虛擬環境步驟；Codex 建立 `skills/course-material-authoring/` 與第 9 週；Claude 完成第 9 週。
- 2026-07-21／07-22：週資料夾重整；第 5–7 週 Codex 主線確立；第 6 週可讀性與 Pydantic 補強；第 7 週 Streamlit 概念導入；第 8 週七項決策定案，兩版產出。
- 2026-07-14／07-15：第 4、5 週兩版比較與整合；第 7 週定位為 Streamlit。

## 下一步建議（同步 Codex，另附 Claude 版項目）

- 第 5、6 週 150 分鐘雙版：在新的 Colab runtime 驗證安裝、Secrets 授權／重啟、一般與串流回應、Structured／Pydantic 成功與失敗及逾時處理，記錄 OpenAI SDK／Pydantic 版本後固定安裝指令，依實測調整 60 秒設定；以教學帳號確認第 6 週 G、A、B/C 流程與授課時間。
- 第 12 週語音輸入與輸出增補及主課綱同步規劃（尚未開始，需使用者指定）。
- 上傳第 3、4、6 週學生版到 Colab 測試顯示與 API 執行；產生第 3、4、6 週投影片或講義版 Markdown；整理 OpenAI／Gemini／Claude 三版一頁對照表。
- 第 7 週：以測試用 key 啟動 `week07/week07_streamlit_app/`，用兩輪追問、清空紀錄、串流／非串流切換確認真實行為。
- 第 8 週：分別執行 starter 與 example summarizer，確認 structured output 與畫面。
- 第 9 週：以文字型 PDF、掃描 PDF、含表格 DOCX、UTF-8／CP950 CSV 測 reader 與錯誤訊息，再測 Streamlit chunk 參數、預覽、JSON 下載與按鈕式摘要。
- 第 10 週：先用 `sample_data/ai_course_faq.md` 跑離線索引與 top-k，再關閉離線模式測真實 Embeddings；ChromaDB preview 需安裝 `requirements-chroma.txt`。
- 第 11 週：依 `docs/課堂環境與部署指南.md` 用 Python 3.12，先用 `sample_data/course_handbook.md` 測離線 embedding、ChromaDB、有答案／無答案／提示注入三種問題，再測真實 API，確認 `[來源 n]` 對應 UI 實際 chunk；再評估 Community Cloud 的 ChromaDB 安裝與記憶體。
- 第 12 週：在 Python 3.12 新環境安裝 `week12_vision_app/requirements.txt`，產生示範收據後測四種模式與錯誤分流，再以測試 key 檢查真實 Vision 回應、detail 差異與 usage；Colab、瀏覽器與 Community Cloud 驗證；只用無敏感資料。
- （Claude 版，選做）若要讓 Claude 參考版與正式版一致：第 10、11 週 ChromaDB 改 `configuration` 寫法、固定 requirements 版本；第 12 週建議 Codex 吸收的項目見比較文件第五節。Claude 版目前只作比較／備援，未經使用者指示不主動改動。
- 產生第 4～12 週投影片。
