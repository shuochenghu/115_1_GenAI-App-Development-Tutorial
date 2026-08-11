# 第 11 週教材比較：Claude 版 vs Codex 版

**主題**：RAG 基礎與文件問答（檢索 → context → grounded answer → 來源引用 → 分層評估）  
**更新日期**：2026-08-11（Claude 品質修正版與 Codex 正式版再次驗證後）

比較對象：

- Claude 版：`生成式AI應用開發_第11週_RAG基礎與改良_教師版/學生版_Claude生成.ipynb` + `week11_rag_qa_claude/`
- Codex 版：`生成式AI應用開發_第11週_RAG基礎與文件問答實作教材_教師版/學生版.ipynb` + `week11_rag_app/`

---

## 一、更新後結論

Claude 版已修正前一輪發現的主要品質問題，現在可作為可執行的精簡替代教材，不再只是有格式缺陷的比較稿。正式課程仍採 Codex 版，原因是它直接銜接 ChromaDB、核心練習與完整 pipeline 較完整，且 Streamlit 專案的狀態管理、結果保留與環境建置較成熟。

整合策略維持：**Codex 為正式主線，Claude 保留為參考；吸收 Claude 的檢索層評估與門檻觀察，不取代正式教材架構。**

---

## 二、Claude 修正確認

| 原問題 | 目前結果 |
|---|---|
| 文字 cell 使用非標準 `cell_type: "md"` | 已改為標準 `markdown` |
| 學生版 Run All 在 `run_local_checks()` 中斷 | 已改為完成 TODO 後由學生主動執行，Run All 不再中斷 |
| 索引簽章只使用檔名與檔案大小 | 已加入檔案內容 SHA-256 |
| slider 變動會自動重建索引 | 已改成按「建立／更新索引」才執行 |
| README 寫著 Codex 尚未產出且 helper 名稱過期 | 已更新為目前版本與對齊後 API |

修正後的 Claude 學生版與教師版皆可解析 JSON、cell id 不重複、輸出清空、普通 code cell 通過 AST；無付費 API 的依序執行也未發生錯誤。

---

## 三、教材結構比較

| 面向 | Claude 版 | Codex 正式版 |
|---|---|---|
| Notebook cells | 32（13 code） | 40（23 code） |
| Notebook 檢索 | 離線假 embedding + cosine，概念自足 | ChromaDB 正式主線；缺套件時用靜態結果銜接後續練習 |
| API key 需求 | 離線檢索不需 key；生成需 key | 固定向量的 ChromaDB 示範不需 key；生成與 OpenAI embedding 才需 key |
| 學生任務 | 2 個核心 TODO + 檢索評估、門檻過濾、App 挑戰 | context、prompt、來源、兩層評估、完整 pipeline |
| 評估 | `evaluate_retrieval` + `evaluate_rag_answer` | 已整合 `evaluate_retrieval` + `evaluate_rag_answer` + 門檻敏感度 |
| 教學節奏 | 精簡，適合作為備援或複習 | 分段完整，符合正式 40-cell 課堂模式 |
| 下一週銜接 | Vision API | Vision API |

### Notebook 檢索方式

- **Codex**：直接示範 ChromaDB 的 collection、metadata、distance 與查詢結果正規化，與正式 App 一致。若環境沒有 `chromadb`，會略過資料庫實跑並使用靜態查詢結果，讓學生仍能完成 context、prompt、引用與評估練習。
- **Claude**：使用離線假 embedding 與手動 cosine retrieval，不需安裝 ChromaDB 就能理解檢索與 context；正式專案再切換到 ChromaDB，因此 Notebook 與 App 的檢索實作不同。

### 練習設計

- **Codex**：學生逐步完成 RAG 核心函式，最後用可注入假檢索、假生成的 pipeline 做無金鑰測試。正式版已吸收 Claude 的優點，在練習 D 加入 `evaluate_retrieval()`，並比較多組 `min_score` 的保留片段數。
- **Claude**：核心 given 較多，練習集中在檢索命中率、分數門檻與 App 改良，負擔較低但對完整 pipeline 的親手實作較少。

---

## 四、共通與未完全對齊處

兩版 `rag_utils.py` 的核心 API 與 hits 扁平資料結構已對齊：

- `build_rag_context`
- `build_rag_prompt`
- `generate_rag_answer`
- `format_sources`
- `evaluate_rag_answer`
- `answer_from_hits`
- `DEFAULT_GENERATION_MODEL`
- `INSUFFICIENT_EVIDENCE_MESSAGE`

兩版也都要求只依 context 回答、把文件內指令視為不可信任資料、證據不足時拒答，並以 `[來源 n]` 對應實際 hits。

Embedding 層仍保留各自第 10 週命名：

- Claude：`build_chroma_collection()` / `query_chroma()`
- Codex：`build_chroma_index()` / `query_chroma_index()`

這一層不強制改名，避免破壞各版本與第 10 週教材的連續性。

---

## 五、Streamlit 專案比較

兩版現在都使用檔案內容雜湊，且只有使用者按下按鈕才建立索引，因此一般 widget rerun 不會自動產生索引費用。

Codex App 仍較完整：

- 使用 `st.segmented_control` 清楚區分 embedding 模式。
- 使用 `st.form` 批次提交問題。
- 將 embedding model 納入索引簽章。
- 保存 chunks、清理後文字與最後一次結果，rerun 後仍可顯示答案。
- 提供索引 metrics 與 chunk 預覽。
- 查詢前以 `collection.count()` 限制 `n_results`。

Claude App 已改善建索引流程，但仍有下列差異：

- `rag_last_result` 已初始化，問答結果卻未寫入與重新渲染，widget rerun 後答案會消失。
- 問答使用 `text_input + button`，未使用 form。
- 索引簽章未包含 embedding model。
- 離線模式固定只顯示檢索與 context，無法搭配真實生成 API 測試完整 RAG。
- README 尚未加入虛擬環境步驟，`requirements.txt` 也未限制主要套件版本。

---

## 六、正式整合結果

本次已將 Claude 版最值得保留的兩項教學設計整合到 Codex 正式 Notebook，且不增加 cell 數：

1. **檢索層評估**：新增 `evaluate_retrieval(test_cases, retrieve_fn, top_k)`，把 Retrieval 與 Generation 錯誤分開定位。
2. **門檻敏感度**：用多組 `min_score` 觀察保留片段數，說明門檻太低會混入雜訊、太高會漏掉正確證據。

正式版仍保留 ChromaDB 主線、學生／教師分離、40-cell 結構與完整 RAG pipeline。Claude 檔案維持原位，作為精簡版本與設計比較，不直接修改成正式版複本。

---

## 七、一句話總結

> **Claude 修正版已可使用，優勢是精簡與離線檢索；Codex 版則在 ChromaDB 連貫性、核心實作、狀態管理與環境可重現性上較完整。正式課程採 Codex 主線，並已吸收 Claude 的檢索評估與門檻敏感度練習。**
