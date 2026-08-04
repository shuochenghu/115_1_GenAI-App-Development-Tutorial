# 第 9 週教材比較：Claude 版 vs Codex 版

**主題**：文件處理與資料前處理（PDF/Word/CSV/TXT/MD 讀取、清理、chunking）
**比較日期**：2026-08-04
**比較對象**：
- Claude 版：`生成式AI應用開發_第09週_文件處理與資料前處理_教師版/學生版_Claude生成.ipynb` + `week09_document_processor_claude/`
- Codex 版：`生成式AI應用開發_第09週_文件處理與資料前處理實作教材_教師版/學生版.ipynb` + `week09_document_processor/`

---

## 一、總覽

| 面向 | Claude 版（`_Claude生成`） | Codex 版（`_實作教材_`） |
|---|---|---|
| 教師版 cells | 36 | 34 |
| 學生版 cells | 36 | 34 |
| 學生核心練習任務 | **6**（3 核心 + 3 練習） | **3**（僅 3 練習） |
| TODO 失敗方式 | 多數採 graceful（回傳 `[]`/`{}`/passthrough），部分練習仍中斷 | 練習 stub 採 `raise NotImplementedError`，核心管線完整可跑 |
| 視覺風格 | emoji 標題 + HTML `<div>` 提示框 | 標準 markdown 表格 + 少量醒目提醒 |
| docstring | 輕量 + markdown callout 補充 | 結構化繁中教學格式（參數/回傳/可能錯誤/教學重點/實作提示） |
| 專案資料夾 | `week09_document_processor_claude/` | `week09_document_processor/` |
| `.streamlit/config.toml` | 有 | 有，已將上傳限制對齊 8 MB |

> 現況校正：本比較檔最初建立後，Codex 正式版已吸收部分 Claude 優點，包括
> `.streamlit/config.toml`、8 MB 上傳限制說明、sidebar helper，以及更完整的繁體中文教學型註解。
> 因此後續建議以「保留正式 Codex 主線，少量吸收 Claude 教學呈現」為準。

---

## 二、最大差異：TODO 策略（教學取向不同）

這是兩版的核心分野。

### Codex：核心管線全部給完整
`decode_text_bytes`、`extract_pdf_text`、`extract_docx_text`、`extract_csv_text`、
`extract_text`、`clean_text`、`chunk_text`、`summarize_document` 在學生版都是
**完整可讀的參考程式**；學生只需完成 **3 個練習**：
`chunk_by_paragraph`、`build_document_report`、`challenge_plan`。

- **取向**：「讀完整範例 → 延伸應用」，摩擦低、示範導向。
- **適合**：進度較緊或程度落差大的班級，把時間留給練習與 App 改造。

### Claude：核心技能挖空
`clean_text`、`chunk_text`、`summarize_document` **三個核心函式留 TODO**，
再加 3 個練習，共 **6 個 TODO**。

- **取向**：「動手實作管線本身」，學生親手寫清理與 chunking 邏輯。
- **適合**：練習量大、參與度高，對核心概念理解更深。

### 失敗設計也不同

| | Codex | Claude |
|---|---|---|
| 未完成 TODO 的行為 | 練習 stub 用 `raise NotImplementedError` 明確提醒尚未完成 | 多數核心 TODO 採 graceful degradation，部分練習仍會中斷 |
| 下游 demo | 核心管線完整，因此主要 demo 可執行；練習 cell 需完成才可執行 | 未完成核心 TODO 時仍可看到部分流程，但結果可能是空資料或 passthrough |
| 自我驗證 | — | `run_local_checks()` 完成後才通過（AssertionError 即回饋） |

---

## 三、相同的地方（兩版可互換）

- **helper 命名與函式簽名完全一致**（Claude 已刻意對齊 Codex 主線）：
  `extract_text` / `clean_text` / `chunk_text` / `get_secret` / `summarize_document`。
- **核心邏輯相同**：
  - 編碼 fallback：`utf-8-sig` → `utf-8` → `cp950`
  - PDF 逐頁抽取並保留 `[第 N 頁]` 來源標記
  - DOCX 讀取段落 + 表格
  - CSV 保留欄名、限 200 列
  - 滑動視窗 chunking（含 `chunk_id` / `start` / `end` / `text`）
- **App 功能幾乎相同**：上傳 → 抽取/清理/chunking → metrics → 預覽/Chunks/匯出分頁 → 按鈕觸發 AI 摘要 → 8 MB 限制。
- **安全與成本原則一致**：`.env` / Streamlit secrets、`.gitignore` 排除機密、上傳不自動花錢。
- **三題練習題目相同**：A 段落優先切割、B 文件品質報告、C Streamlit 改造。

---

## 四、各自優點

### Codex 版強項
- 結構化 docstring（參數 / 回傳 / 可能錯誤 / 教學重點）本身就是教材，可讀性高。
- 核心給完整 → 課堂時間集中在練習與 App，適合進度緊湊或程度落差大的班級。
- 每個 reader 都有「為什麼這樣做」的行內註解。
- 使用標準 `markdown` cell type，較適合作為正式 Jupyter / Colab 教材。

### Claude 版強項
- 6 TODO 讓學生**親手實作核心管線**，對「清理」「chunking」理解更深。
- graceful degradation → 未完成 TODO 也能跑，除錯體驗較友善。
- emoji + HTML callout 提示框視覺層次清楚，重點（安全 / 成本 / 限制）更醒目。
- 可作為高挑戰班級的補充版本，讓學生親手實作 `clean_text()` 或 `chunk_text()`。

---

## 五、整合建議（沿用第 5 週整合模式）

以任一版為底、互取所長：

1. **TODO 分量做成「可調」**：正式學生版預設用 Codex 的「核心給完整、只練 3 題」降低摩擦；
   對程度好的班級，在補充說明中加入「重寫 `clean_text()` 或 `chunk_text()`」的進階挑戰。
   → 這是最值得統一的決策點。
2. **失敗策略不要全面改成 graceful degradation**：正式 notebook 的練習 stub 保留
   `NotImplementedError`，讓學生清楚知道哪裡尚未完成；若改成 App 互動功能，再用
   `st.warning()` / `st.error()` 顯示友善錯誤。
3. **docstring 採 Codex 的結構化格式**（參數 / 回傳 / 可能錯誤），比 Claude 的輕量
   docstring 更適合當參考教材。
4. **視覺少量吸收 Claude 的 callout**：只放在安全、成本、OCR / 格式限制等紅線位置，
   避免整份 notebook 變成過度裝飾。
5. **README 維持初學者友善**：安裝步驟應明確先 `cd week09/week09_document_processor`，
   再安裝套件與啟動 Streamlit。

---

## 六、一句話總結

> **Codex 版是「完整參考教材 + 精準延伸練習」，Claude 版是「動手實作核心 + 友善除錯體驗」。**
> 兩版 helper 與功能完全對齊，可自由互換或整合；主要取捨在「學生要不要親手寫核心管線」。
