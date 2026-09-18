# 第 12 週教材比較：Claude 版 vs Codex 版

**主題**：多模態應用：Vision API 與圖片理解（圖片驗證 → Base64 → Responses API `input_image` → prompt 設計 → Structured Outputs 抽取 → 錯誤分流 → Streamlit 圖片理解工具）
**更新日期**：2026-09-16（Claude 版首次產出，Codex 版同日產出、尚未 commit）

比較對象：

- Claude 版：`生成式AI應用開發_第12週_多模態應用_Vision_API與圖片理解_教師版/學生版_Claude生成.ipynb` + `week12_vision_app_claude/`
- Codex 版：`生成式AI應用開發_第12週_多模態應用_Vision_API與圖片理解實作教材_教師版/學生版.ipynb` + `week12_vision_app/`

---

## 一、結論

兩版主線完全一致：OpenAI Responses API + `input_image`（Base64 data URL）、四種任務模式、JSON Schema strict 抽取、refusal / status 分流、`store=False`、8 MB 與 2,000 萬像素上限、安全紅線相同。

**Claude 版是在 Codex 專案 `vision_utils.py` 的 API 之上做的對齊版**，helper 命名與函式簽名相同，兩版可互換對照。Claude 版的差異集中在三處：Notebook 與專案的函式名統一、離線示範模式、失敗案例（模糊收據）。

依既有決策，正式課程仍以 Codex 版為主線；Claude 版作為備援與比較。建議 Codex 版吸收 Claude 版的「Notebook 與專案命名統一」與「模糊版測試圖片」兩項。

---

## 二、教材結構比較

| 面向 | Claude 版 | Codex 版 |
|---|---|---|
| Notebook cells | 40（17 code） | 40（22 code） |
| 學生 TODO | 2 核心（`validate_image`、`build_task_prompt`，graceful degradation）+ 練習 A `choose_detail`、B `normalize_receipt`、C `evaluate_vision_answer`（`NotImplementedError` + 註解 demo）+ D `challenge_plan` | 練習 A `validate_upload`、B `choose_detail`、C `normalize_receipt`、D `evaluate_vision_answer`（回傳 placeholder 骨架） |
| Notebook 與專案函式名 | **一致**（`validate_image` / `analyze_image` 直接來自 `vision_utils.py`） | **不一致**：Notebook 用 `validate_upload(file_bytes, filename)` / `analyze_image_bytes` / `extract_receipt`，專案用 `validate_image(file_bytes)` / `analyze_image(mode=)` |
| 不需 API key 可做的事 | 驗證、Base64、prompt、request 預覽、**離線示範結果**、`run_local_checks` | 驗證、Base64、prompt、schema 閱讀、練習 smoke test |
| 測試圖片 | 清楚版 + **模糊旋轉版**（示範 null / warnings） | 清楚版 |
| 自我檢查 | `run_local_checks()`（學生版註解，避免 Run All 中斷） | 各練習附 assert smoke test（學生版骨架可通過，尺寸在完成後才正確） |
| Claude Vision 補充 | 一個 markdown 對照表（選讀，不執行） | 無 |
| 環境說明 | 未固定版本 | 固定版本（openai 2.49 / pillow 12.3 / streamlit 1.63），引用課堂環境指南 |
| 下週銜接 | Function Calling | Function Calling |

### 學生任務設計

- **Codex**：四題練習都是回傳 placeholder 的骨架，學生版 Run All 一定不中斷；但 `validate_upload` 骨架固定回 `"image/png"` 與 0×0，練習完成前的 smoke test 只驗檔名與 bytes 數。
- **Claude**：核心兩題採 graceful degradation（骨架仍做最少檢查、回通用 prompt），練習三題用 `NotImplementedError` 加註解 demo，完成後由 `run_local_checks()` 驗收。負擔與 Codex 相當，但把「驗證」與「prompt」提升為核心技能，與第 9～11 週「輸入驗證、只依證據回答」的主軸對齊。

### 教學設計差異

- **離線示範模式**：Claude 版 `analyze_image(..., offline=True)` 跑完驗證與 prompt 後回傳明確標註「不是模型分析結果」的固定樣本；App 側邊欄可勾選。沒有金鑰的學生可走完整個 UI 流程。Codex 版在缺金鑰時只能看驗證與預覽。
- **request 預覽**：Claude 版 `build_request` + `preview_request` 把「將送出的結構」印出來（data URL 截短、schema 略），對應學習目標「看懂圖片輸入資料流」。Codex 版把 request 組裝內嵌在 `analyze_image`，學生看程式碼理解。
- **失敗案例**：Claude 版用模糊旋轉收據示範「好的結果是 null + warnings」，對應檢核清單「記錄一個 Vision 看錯的案例」。Codex 版把這件事放在課後任務。

---

## 三、Streamlit 專案比較

兩版都是：上傳 → 本機驗證與預覽 → `st.form` 送出才呼叫 API → 結果存 `session_state` → 抽取模式顯示欄位、品項表格、warnings 與 JSON。

| 面向 | Claude 版 | Codex 版 |
|---|---|---|
| 控制項 | `st.radio` / `st.selectbox`（保守，相容舊版） | `st.segmented_control`（需較新 Streamlit） |
| detail 預設 | 依任務模式用 `choose_detail()` 給建議值 | 固定 `auto` |
| 離線模式 | 有（不呼叫 API，樣本結果標註） | 無 |
| request 預覽 | 可勾選「送出前顯示 request 結構」 | 無 |
| 抽取結果顯示 | 先經 `normalize_receipt()` 再顯示 | 直接讀 `result[...]`（schema strict 保證欄位存在） |
| 測試圖片腳本 | 清楚版 + 模糊版 | 清楚版 |
| README | 功能、安全、建議測試 5 步 | 加上虛擬環境步驟、constraints 快照、部署入口表 |

---

## 四、共通與對齊處

兩版 `vision_utils.py` 的核心 API 一致：

- `DEFAULT_MODEL` / `MAX_FILE_BYTES` / `MAX_IMAGE_PIXELS` / `SUPPORTED_MIME_TYPES` / `RECEIPT_SCHEMA`
- `get_secret` / `create_client`
- `detect_image_mime` / `validate_image` / `image_to_data_url`
- `build_task_prompt(mode, question)`
- `get_refusal_reason` / `require_completed_response`
- `analyze_image(file_bytes, *, mode, question, detail, model)` → `str | dict`

Claude 版額外提供（Codex 版沒有，但不影響互換）：

- `build_request` / `preview_request` / `offline_demo_result`
- `analyze_image(..., offline=False)` 多一個 keyword 參數
- `choose_detail` / `normalize_receipt` / `evaluate_vision_answer`（Codex 版只在 Notebook 定義，未放進專案）
- 常數 `TASK_MODES` / `DETAIL_LEVELS` / `OFFLINE_DEMO_NOTICE` / `SYSTEM_INSTRUCTIONS`

---

## 五、建議 Codex 版吸收的項目

1. **Notebook 與專案函式名統一**：把 Notebook 的 `validate_upload` / `analyze_image_bytes` / `extract_receipt` 改成專案的 `validate_image` / `analyze_image(mode=)`，學生從 Notebook 到 App 不必重新對照（第 11 週已有同樣的教訓）。
2. **模糊版測試圖片**：`create_demo_receipt.py` 多產一張模糊旋轉版，讓課堂能當場示範 null / warnings。
3. **練習 helper 放進專案**：`choose_detail` / `normalize_receipt` 放進 `vision_utils.py` 並在 App 使用，練習成果才會出現在 App 裡。

Claude 版可向 Codex 版借入：固定套件版本與課堂環境指南連結、README 的部署入口表。

---

## 六、驗證狀態

Claude 版（2026-09-16）：

- 兩版 Notebook：JSON 解析、`cell_type` 合法、cell id 無重複、`ast` 無 SyntaxWarning、無亂碼、學生版 6 個 TODO cell、`run_local_checks()` 在學生版為註解。
- 教師版與學生版所有 code cell **依序離線執行 0 錯誤**（含 Pillow 產圖、驗證負例、data URL、request 預覽、離線示範、`run_local_checks` ✅、練習 A/B/C 驗收）。
- `vision_utils.py` / `app.py` / `create_demo_receipt.py` 通過 `py_compile`；`vision_utils` 離線煙霧測試通過（空檔、假副檔名、損壞檔、過大檔、動態 GIF 全被擋下；refusal / incomplete / 空輸出分流正確）。
- Streamlit `AppTest`：初始畫面缺金鑰提示、模式切換後 detail 建議變 high、離線模式切換皆無例外。`file_uploader` 無法在 AppTest 模擬上傳，上傳後流程以 `vision_utils` 測試涵蓋。
- 付費 Vision API 與瀏覽器 `streamlit run` 未列入正式驗證。測試期間因本機環境已設定 `OPENAI_API_KEY`，`analyze_image` 曾意外真實呼叫一次（單張小圖、圖片描述模式，成功回傳）；之後的測試都把金鑰清空。這次意外呼叫附帶確認了 `input_image` + data URL 在目前 SDK 可用。

Codex 版：本文件未實跑，僅做靜態閱讀比較。

---

## 七、一句話總結

> **兩版主線與 helper API 一致；Claude 版多了離線示範、request 預覽與模糊收據失敗案例，且 Notebook 與專案命名統一；Codex 版在環境固定與部署說明上較完整。正式課程維持 Codex 主線，建議吸收 Claude 版的命名統一與模糊版測試圖片。**
