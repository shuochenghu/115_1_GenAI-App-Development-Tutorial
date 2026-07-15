# 專案工作記憶

此檔用來保存可隨專案移動的工作狀態，方便在不同電腦或不同 AI 工具中接續處理。請勿在此檔寫入 API key、密碼、信用卡、學生個資或其他機密資料。

## 專案定位

本資料夾是 115 學年度上學期課程大綱與教材工作區，主要正在製作「生成式AI應用開發」課程教材。課程主線以 Python、OpenAI API、Google Colab、Streamlit 為核心；Claude API 與 Gemini API 作為比較或補充版本，不作為主要教學主線。

## 目前教材狀態

目前 notebook 教材只保留「學生版」與「教師版」。原始版 notebook 已刪除，避免和教師版內容重複。

- `生成式AI應用開發_16周課程大綱.md`：課程主大綱，目前實際規劃為 18 週，含 16 週授課與第 17、18 週自主學習。
- `生成式AI應用開發_第02週_Python複習_學生版.ipynb`：第 2 週學生版，保留 TODO 骨架。
- `生成式AI應用開發_第02週_Python複習_教師版.ipynb`：第 2 週教師版，保留完整參考答案。
- `生成式AI應用開發_第03週_OpenAI_API入門_學生版.ipynb`：第 3 週 OpenAI API 學生版，保留 TODO 骨架。
- `生成式AI應用開發_第03週_OpenAI_API入門_教師版.ipynb`：第 3 週 OpenAI API 教師版，保留完整參考答案。
- `生成式AI應用開發_第03週_Gemini_API入門_學生版.ipynb`：第 3 週 Gemini API 學生版，保留 TODO 骨架。
- `生成式AI應用開發_第03週_Gemini_API入門_教師版.ipynb`：第 3 週 Gemini API 教師版，保留完整參考答案。
- `生成式AI應用開發_第03週_Claude_API入門_學生版.ipynb`：第 3 週 Claude API 學生版，保留 TODO 骨架。
- `生成式AI應用開發_第03週_Claude_API入門_教師版.ipynb`：第 3 週 Claude API 教師版，保留完整參考答案。
- `生成式AI應用開發_第04週_Prompt_Engineering_教師版.ipynb`：第 4 週 Prompt Engineering 教師版，保留完整參考答案（35 cells）。
- `生成式AI應用開發_第04週_Prompt_Engineering_學生版.ipynb`：第 4 週 Prompt Engineering 學生版，四大功能與課堂練習保留 TODO 骨架。
- `生成式AI應用開發_第04週_Prompt_Engineering實作教材_教師版.ipynb`：依原規劃重建的 40-cell 教師版，包含完整參考答案。
- `生成式AI應用開發_第04週_Prompt_Engineering實作教材_學生版.ipynb`：依原規劃重建的 40-cell 學生版，三組綜合練習保留 TODO 骨架。
- `生成式AI應用開發_第05週_對話狀態_Streaming與聊天機器人實作教材_教師版.ipynb`：第 5 週 40-cell 教師版，包含完整聊天 session、Streaming 與三組練習答案。
- `生成式AI應用開發_第05週_對話狀態_Streaming與聊天機器人實作教材_學生版.ipynb`：第 5 週 40-cell 學生版，三組綜合練習保留 TODO 骨架。
- `生成式AI應用開發_第06週_Structured_Outputs_JSON_Schema與資料抽取實作教材_教師版.ipynb`：第 6 週 40-cell 教師版，包含 Structured Outputs、JSON Schema、資料抽取、Pydantic、巢狀模型、refusal handling 與練習答案。
- `生成式AI應用開發_第06週_Structured_Outputs_JSON_Schema與資料抽取實作教材_學生版.ipynb`：第 6 週 40-cell 學生版，保留 JSON Schema、Pydantic 與重試練習 TODO 骨架。
- `生成式AI應用開發_第07週_Streamlit_Web_App入門實作教材_教師版.ipynb`：第 7 週 40-cell 教師版，主軸為 VS Code、本機 Python、Streamlit、OpenAI Responses API、session state、streaming、secrets、表單與檔案上傳。
- `生成式AI應用開發_第07週_Streamlit_Web_App入門實作教材_學生版.ipynb`：第 7 週 40-cell 學生版，保留 Streamlit App、API helper、session state、streaming 與期中小專題規劃 TODO。
- `week07_streamlit_app/`：第 7 週可直接用 VS Code 開啟的 Streamlit 範例專案，包含 `app.py`、`requirements.txt`、`.env.example`、`.gitignore`、`README.md` 與 `.streamlit/secrets.example.toml`。

## 最近工作進度（2026-07-15）

- 進度紀錄點：第 6 週正式 40-cell 教師版與學生版已生成並完成 Claude 版本比較；正式版保留為主線，吸收 Claude 版的 Pydantic 欄位驗證表格、巢狀 `MeetingMinutes` 範例、`extract_structured()` wrapper 與 refusal handling 提醒。
- 第 6 週正式版與 Claude 生成版比較結論：正式版教學節奏較完整，適合保留 JSON Schema first；Claude 版較偏 Pydantic-first，只吸收適合 App 開發的補強點，不取代正式教材架構。
- 第 6 週學生版仍保留 TODO 分離；教師版提供完整答案。兩版皆維持 40 cells，付費 API cells 預設關閉。
- 第 7 週教材已依課程大綱改為「Streamlit Web App 入門」，不是 Git 主題；現有 `生成式AI應用開發_第07週_Git實作教材.md` 保留作為 GitHub Desktop、GitHub 與 Streamlit Community Cloud 部署補充。
- 第 7 週正式教材採 notebook 作為教材與步驟說明，實作成果改為本機 `week07_streamlit_app/` 專案；學生需在 VS Code 中執行 `streamlit run app.py`。
- 第 7 週 notebook 與 `week07_streamlit_app/README.md` 已補上銜接對照表，明確標示每個 notebook 章節對應到 VS Code 專案中的 `app.py`、`requirements.txt`、`.env.example`、`.gitignore`、`README.md` 與 Streamlit 功能區塊。
- 2026-07-15 已同步 Codex 長期記憶更新：第 7 週教材定位、notebook / VS Code 專案雙軌銜接、40-cell 狀態、TODO 分離與 Responses API + Streamlit streaming 主線。

- 歷史紀錄點：第 4、5 週教材已完成建立、Claude 版本比較與優點整合，之後已接續完成第 6 週教材。
- 已比較第 4 週 40-cell 教師版與 Claude 生成版本，決定保留 40-cell 實作教材為主線，吸收 Claude 版的參數化函式與 prompt 並排比較優點。
- 第 4 週教師版與學生版已同步改良：補強 API key preflight、API 錯誤處理、`compare_prompts()`、摘要／分類／改寫／問答參數化、分類契約與字數檢查，以及預設關閉的批次付費測試。
- 第 4 週教師版保留完整答案與 baseline 觀察提示；學生版只在客服分類、初學者改寫與課程規定問答保留 TODO，兩版共用 cell 已對齊。
- 第 5 週教師版與學生版已新建完成，檔名採 `課程名稱_第NN週_主題實作教材_教師版／學生版.ipynb`，兩版皆為 40 cells。
- 第 5 週已完成多輪對話、手動 history、有限 context、簡易記憶、usage、reset、Streaming events、串流聊天 session、console chatbot 與三組練習。
- 第 5 週已依 Claude 版本的優點再次補強：學習目標改為「能力／後續應用」對照表、加入 `history_size()`、預設關閉的 `max_turns=1` 遺忘實驗，以及 Streaming 部分輸出的內容審核提醒；教師版與學生版維持 40 cells 且 TODO 分離不變。
- 第 5 週最終驗證結果：教師版與學生版皆為 40 cells、40 個唯一 cell IDs、26 個 Markdown cells、14 個 code cells，靜態語法與 JSON 解析通過，無執行輸出；教師版無 TODO，學生版只保留封面說明與原訂三組練習 TODO。
- 第 4、5 週的付費 API cells 尚未實際執行；目前已完成 JSON、cell ID、靜態語法、TODO 分離、教師／學生對齊與中文亂碼檢查。
- 第 4、5、6 週的付費 API cells 尚未實際完整執行；可先將學生版上傳 Colab 做顯示與實際 API 測試。

## 已完成的重要決策

- 第 2 週定位為 API 開發前的 Python 快速複習，內容包含函式、f-string、list / dict、JSON、例外處理、API key 管理與公開 API 呼叫。
- 第 2 週已分成學生版與教師版；學生版不直接提供主要練習答案。
- 第 2 週第六節已補上 Colab Secrets、環境變數設定、PowerShell、`setx`、macOS / Linux `export` 等 API key 設定方式。
- 曾發生 Colab / Windows 編碼流程造成中文被寫成大量 `?` 的問題；目前 notebook 需用 JSON Unicode escape 格式輸出以降低風險。
- 第 3 週 OpenAI API 版本主線使用 Responses API：`client.responses.create()` 與 `response.output_text`。
- 第 3 週 OpenAI API 預設模型已由 `gpt-5.5` 改為 `gpt-5.4-mini`，並保留 `OPENAI_MODEL` 環境變數覆蓋機制。
- 第 3 週 OpenAI API 版本已補上多輪對話示範：使用 `previous_response_id=response1.id` 延續上一輪 Responses API 對話。
- 第 3 週第十節已補強為三題：練習 A「Python 作業批改助教」、練習 B「usage 與費用估算」、練習 C「自由設計角色與 instructions」。
- 第 3 週另產生 Gemini API 與 Claude API 版本，用於跨平台比較。
- Gemini 版本使用 `google-genai`、`GEMINI_API_KEY`、`client.interactions.create()`、`system_instruction`、`interaction.output_text`、`previous_interaction_id`。
- Claude 版本使用 `anthropic`、`ANTHROPIC_API_KEY`、`client.messages.create()`、top-level `system`、`message.content[0].text`，並強調 Claude Messages API 每次需送出完整 messages history。
- 第 3 週三個平台的多輪對話比較：OpenAI 使用 `previous_response_id`，Gemini 使用 `previous_interaction_id`，Claude 送出完整 `messages` history。
- 第 3 週 OpenAI / Gemini / Claude 的學生版與教師版已做 markdown text cell 視覺美化：標題加入少量 emoji，學習任務、安全提醒、課堂練習與成本提醒加入 HTML 提示框。
- Colab 對 markdown cell 的 CSS `style` 支援不穩定；若要讓文字顏色更容易顯示，優先使用 `<font color="..."><b>文字</b></font>` 標示重點詞。
- 第 4 週 Prompt Engineering 為 OpenAI 主線（依課程大綱，不再做三平台版本），延續第 3 週的 Responses API 與 `ask_ai_safe(user_input, role=...)`（role 即 instructions/system prompt）。
- 第 4 週涵蓋：system prompt/角色設定、任務拆解、輸出限制與格式控制、few-shot（用 role/content 清單放範例對）、prompt 測試（`compare_prompts()`），實作 `summarize` / `classify` / `rewrite` / `answer_question` 四大功能。
- 第 4 週 `answer_question` 採「只依參考資料回答、找不到就說找不到」設計，作為第 11 週 RAG 的雛形。
- 第 4 週學生版將四大功能函式與三題課堂練習（A 會議記錄整理、B few-shot 垃圾郵件分類、C 選做 prompt 測試）保留 TODO；示範用的 demo cell（第二～六節）兩版皆完整可執行。
- 第 4 週沿用第 3 週 markdown 風格與 emoji/HTML 提示框；沿用預設模型 `gpt-5.4-mini`（`OPENAI_MODEL` 可覆蓋）。
- 第 4 週「實作教材」兩版已重建為 40 cells，包含三小時流程、baseline 對照、Prompt 五元素、`instructions` / `input` 分工、Markdown / XML 分隔、任務拆解、few-shot、四種應用、固定案例測試、版本紀錄、完成檢核與課後任務。
- 第 4 週「實作教材」學生版的客服分類器、初學者改寫器與課程規定問答保留 TODO；教師版提供完整答案。
- 第 4 週「實作教材」兩版已通過 JSON 解析、40-cell 數量、cell ID 唯一性、code cell 靜態語法、關鍵章節、保存輸出、中文問號亂碼與 TODO 分離檢查；付費 API cells 尚未實際執行。
- 未依本次需求修改原有 35-cell 正式版與檔名含 `Claude生成` 的副本；它們與 40-cell「實作教材」版本並存。
- 第 5 週延續 OpenAI Responses API 主線，涵蓋獨立請求、`previous_response_id`、手動 `user` / `assistant` history、有限對話視窗、簡易重要事實記憶、usage、reset 與 Streaming。
- 第 5 週 Streaming 使用 `stream=True`，處理 `response.output_text.delta`、`response.completed` 與 `error`；只有完成事件後才更新 response ID 與正式 transcript。
- 第 5 週提供 `ResponseChatSession`、`StreamingChatSession`、console chatbot、`WindowedMemoryChat` 與 guarded smoke test；互動式 `run_console_chat()` 預設註解，延伸付費練習預設關閉。
- 第 5 週 context 管理同時用 `history_size()` 觀察訊息／字元規模、用回應 `usage` 判讀實際 token，並提供預設關閉的 4-request 遺忘實驗；Streaming 章節明列部分輸出較難審核，正式應用需有審核與中止策略。
- 第 5 週學生版的課程諮詢 Session、delta 計數器與最近 N 輪記憶保留 TODO；教師版提供完整答案。
- 第 5 週兩版已通過 JSON 解析、40-cell 數量、cell ID 唯一性、code cell 靜態語法、教師／學生共用 cell 對齊、關鍵 API 字串、中文亂碼與 TODO 分離檢查；付費 API cells 尚未實際執行。
- 第 6 週延續 OpenAI Responses API 主線，先教 `text.format` + `json_schema` + `json.loads()`，再補充 Pydantic `client.responses.parse()`；不採 Claude 版 Pydantic-first 作為主線。
- 第 6 週 Structured Outputs helper 已加入 refusal / 空 `output_text` 檢查，避免模型拒答時直接 `json.loads()` 或寫入資料庫。
- 第 6 週 Pydantic 補強欄位驗證技巧表格、`ReviewInsight`、`ActionItem`、`MeetingMinutes` 巢狀模型、`parse_with_pydantic()` 與 App 可重用的 `extract_structured()` wrapper。
- 第 6 週學生版的 `ReviewInsight`、客服訊息 JSON Schema、收據資料 Pydantic 與 retry wrapper 保留 TODO；教師版提供完整答案。
- 第 7 週延續 OpenAI Responses API 主線，Streamlit App 範例使用 `client.responses.create()`、`stream=True`、`response.output_text.delta`、`st.write_stream()`、`st.chat_input()`、`st.chat_message()`、`st.session_state` 與 `st.secrets`。
- 第 7 週學生版 TODO 保留在 API key helper、OpenAI helper、session state、Chat UI、streaming、sidebar、表單、檔案上傳、README 與期中小專題規劃；教師版無 TODO。

## 編輯與驗證原則

- 修改 notebook 時，優先用 Python `json` 模組讀寫 `.ipynb`。
- 輸出 notebook 時使用 `json.dumps(..., ensure_ascii=False, indent=1)`，保留可讀的繁體中文；寫入後必須重新解析 JSON 並檢查常見亂碼特徵。
- 修改學生版時，保留 TODO，不要把教師版完整答案貼回學生版。
- 修改教師版時，可保留完整答案與課堂示範程式。
- 之後生成或修改教材中的程式碼時，都要加入適當註解：用註解說明區塊目的、API 呼叫、狀態管理、錯誤處理與安全注意事項；避免逐行解釋顯而易見的語法。
- 每次生成或修改完某一週教材後，必須同步更新本檔的教材狀態、最近工作進度、重要決策或下一步建議，避免專案記憶落後於實際檔案。
- 第 3 週 notebook 的 markdown 風格已採用少量 emoji、HTML 提示框與 `<font color>` 重點標籤；後續新增章節時可沿用此風格，但避免過度使用顏色。
- 每次修改 notebook 後，至少檢查：
  - JSON 可正常解析。
  - code cell 靜態語法檢查通過。
  - 沒有大量 `?` 亂碼 cell。
  - 學生版主要練習仍保留 TODO。

## 模型與環境變數

- OpenAI 版本預設模型：`gpt-5.4-mini`，可用 `OPENAI_MODEL` 覆蓋。
- Gemini 版本預設模型：`gemini-3.5-flash`，可用 `GEMINI_MODEL` 覆蓋。
- Claude 版本預設模型：`claude-haiku-4-5`，可用 `CLAUDE_MODEL` 覆蓋。
- 若任一預設模型在上課帳號不可用，課前改成實際可用模型。

## 下一步建議

- 實際上傳第 3 週學生版到 Colab 測試顯示與 API 執行。
- 比較 OpenAI、Gemini、Claude 三版的 API key、client、輸入格式、回應欄位與多輪對話差異，整理成一頁對照表。
- 產生第 3 週投影片或講義版 Markdown。
- 上傳第 4 週學生版到 Colab 測試顯示與 API 執行。
- 產生第 4 週投影片或講義版 Markdown。
- 上傳第 6 週學生版到 Colab 測試顯示，並實際執行 Structured Outputs 與 Pydantic parse API cells。
- 產生第 6 週投影片或講義版 Markdown。
- 上傳或本機開啟第 7 週教材，測試 `week07_streamlit_app` 是否能在 VS Code terminal 以 `streamlit run app.py` 啟動。
- 可接續製作第 8 週期中個人小專題教材，要求學生基於第 7 週 Streamlit 專案完成一個小型 LLM Web App。
