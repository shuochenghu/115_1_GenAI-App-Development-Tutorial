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
- `生成式AI應用開發_第04週_Prompt_Engineering_教師版_Claude生成.ipynb`：第 4 週教師版（**Claude Code 產出**），35 cells，保留完整參考答案。
- `生成式AI應用開發_第04週_Prompt_Engineering_學生版_Claude生成.ipynb`：第 4 週學生版（**Claude Code 產出**），四大功能與課堂練習保留 TODO 骨架。
- `生成式AI應用開發_第04週_Prompt_Engineering實作教材_教師版.ipynb`：第 4 週教師版（**Codex 產出**）。
- `生成式AI應用開發_第04週_Prompt_Engineering實作教材_學生版.ipynb`：第 4 週學生版（**Codex 產出**）。
- `生成式AI應用開發_第05週_對話與Streaming_教師版_Claude生成.ipynb`：第 5 週教師版（**Claude Code 產出**），33 cells，保留完整參考答案。
- `生成式AI應用開發_第05週_對話與Streaming_學生版_Claude生成.ipynb`：第 5 週學生版（**Claude Code 產出**），33 cells，核心實作與練習保留 TODO 骨架。
- `生成式AI應用開發_第05週_對話狀態_Streaming與聊天機器人實作教材_教師版.ipynb`：第 5 週教師版（**Codex 產出**）。
- `生成式AI應用開發_第05週_對話狀態_Streaming與聊天機器人實作教材_學生版.ipynb`：第 5 週學生版（**Codex 產出**）。
- `生成式AI應用開發_第03週投影片.md`：第 3 週 Marp 投影片，25 頁，OpenAI 主線；內文不提第 4 週，結尾為「課後動手做」；含擴充的 Gemini / Claude API 差異介紹（對照總表 + 各自程式碼寫法 + 多輪對話差異 + 選用建議）。
- `生成式AI應用開發_第06週_Structured_Outputs與資料抽取_教師版_Claude生成.ipynb`：第 6 週教師版（**Claude Code 產出**），31 cells，保留完整參考答案。
- `生成式AI應用開發_第06週_Structured_Outputs與資料抽取_學生版_Claude生成.ipynb`：第 6 週學生版（**Claude Code 產出**），31 cells，8 個 cell 保留 TODO（含版本說明）。

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
- 第 4 週學生版與教師版已通過 JSON 解析、cell ID 唯一性、code cell 靜態語法、保存輸出、中文問號亂碼與 TODO 分離檢查；付費 API cells 尚未實際執行。
- 依需求將第 4 週兩版內容另外儲存為含「實作教材」的新檔名；原始正式檔案保留不變，新檔目前為逐位元相同副本。
- 第 5 週為 OpenAI 主線，成果為「具多輪對話記憶與串流輸出的簡易聊天機器人」，延續第 3 週 `ask_ai_safe()` 與 Responses API、第 4 週 prompt 技巧。
- 第 5 週呈現兩種多輪對話做法並比較：方法 A `previous_response_id`（平台代管）、方法 B 自己維護 `messages` history（可控上下文、跨平台、便於成本控制）；後段採方法 B。
- 第 5 週用 `ChatSession` 類別封裝 `system` 設定、`history` 累積、`_trim()` 只保留最近 `max_turns` 輪、`reset()`。
- 第 5 週 Streaming 用 Responses API `stream=True`，取 `event.type == "response.output_text.delta"` 的 `event.delta` 逐字印出並累加成完整文字。
- 第 5 週聊天機器人 `chat_bot()` 用 `input()` 迴圈 + streaming + 歷史裁切；教師版預設把 `chat_bot()` 呼叫「註解掉」，避免 Colab「全部執行」卡在 input()。
- 第 5 週學生版 TODO 落在 `ChatSession`（cell-16）、`stream_reply`（cell-20）、`chat_bot`（cell-25）、練習 A/B/C（cell-27/29/31）；demo cell（無記憶、previous_response_id、手動 history、成本觀察）兩版皆完整。
- 第 5 週三題練習：A 主題聊天機器人（英文練習夥伴）、B 上下文長度實驗（max_turns=1 觀察遺忘）、C 選做累計整場 token 與估算成本。
- 第 5 週兩版已通過 JSON 解析、cell id 無重複、code cell `ast` 語法、中文亂碼與 TODO 分離檢查；付費 API cells 尚未實際執行。
- 第 3 週投影片內文的第 4 週前向指涉已全數移除（依需求「先不提第四周」），並擴充 Gemini / Claude API 差異段落。
- 第 6 週主題為 Structured Outputs 與資料抽取，延續 OpenAI Responses API 主線；涵蓋純文字回覆的解析困境、JSON Schema 手動定義（`text.format` + `json_schema` + `strict`）、Pydantic 模型定義（`client.responses.parse()` + `text_format` + `response.output_parsed`）、巢狀模型與清單抽取、`ValidationError`/`try except` 錯誤處理、`extract_structured()` 共用抽取函式封裝。已用 WebFetch 對照 OpenAI 官方 Structured Outputs 與 Responses API 文件確認語法正確。
- 第 6 週練習：A 履歷抽取（`ResumeInfo`）、B 訂單抽取（`OrderItem` + `OrderInfo` 巢狀清單並計算總額）、C 選做抽取失敗重試機制（`extract_with_retry()`）。
- 第 6 週 TODO 設計採「模型/函式定義留空、demo 呼叫維持完整」原則：demo cell 一律用 `print(model)` 而非存取特定欄位，避免學生未完成 TODO 時下游 cell 因缺欄位 `AttributeError` 而整個中斷。
- 第 6 週結尾预告 Week 7 為 Git 版本控制與 Streamlit 部署，與既有 `生成式AI應用開發_第07週_Git實作教材.md` 內容一致。

## 編輯與驗證原則

- 修改 notebook 時，優先用 Python `json` 模組讀寫 `.ipynb`。
- 輸出 notebook 時使用 `json.dumps(..., ensure_ascii=True, indent=1)`，降低 Colab 中文亂碼風險。
- 修改學生版時，保留 TODO，不要把教師版完整答案貼回學生版。
- 修改教師版時，可保留完整答案與課堂示範程式。
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

## 第五週兩版比較（2026-07-14）

Claude 版與 Codex 版已完成詳細比較，主要差異如下：

**Claude 版優點**：程式碼初學者友善；以方法 B（自己維護 history）為主線，跨平台通用；`chat_bot()` + `input()` 直觀；emoji/HTML callout 視覺格式清楚。

**Claude 版需修正**：
1. `ChatSession.send()` 缺乏 API 失敗時的狀態保護（未捕捉例外時 history 可能被污染）
2. 無輸入驗證（空白字串直接送 API）
3. `stream_reply()` 無法接上對話歷史，Streaming 與 `ChatSession` 脫節

**Codex 版優點**：API 失敗不更新狀態（正確）；`important_facts` 與對話歷史分離（Week 11 RAG 先備概念）；有課程時間表、測試計畫、完成檢核清單與課後作業。

**Codex 版需調整**：40 cells 對 150 分鐘略多；繼承設計對大三學生偏進階；`RUN_PRACTICE = False` 旗標容易讓學生困惑。

**整合建議**：以 Claude 版結構為底，從 Codex 版借入：失敗不更新狀態的保護寫法、`important_facts` 概念、完成檢核清單與課後作業說明。

## 命名規則（重要）

- `..._Claude生成.ipynb`：Claude Code（本工具）產出
- `...實作教材_....ipynb`：Codex（其他 AI 工具）產出
- CLAUDE.md 已更新此規則，且記憶檔入口已改為 `PROJECT_MEMORY_claude.md`

## 下一步建議

- **第 5 週**：決定是否整合兩版，或直接以 Claude 版為主並套入上述三項修正後推進
- 實際上傳第 3–6 週學生版到 Colab 測試（串流顯示、`input()` 聊天迴圈、Structured Outputs 付費 cells）
- 產生第 4、5、6 週投影片
- 第 6 週目前只有 Claude Code 版本，尚無 Codex 版本可比較；若 Codex 後續也產出第 6 週教材，可比照第 4、5 週流程做優缺點比較與整合
- 接續製作第 7 週：Git 版本控制與 Streamlit 部署實作（已有 `生成式AI應用開發_第07週_Git實作教材.md` 講義可搭配）
