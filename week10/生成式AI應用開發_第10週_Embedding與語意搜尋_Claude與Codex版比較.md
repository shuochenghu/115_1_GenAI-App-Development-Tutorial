# 生成式 AI 應用開發：第 10 週 Embedding 與語意搜尋 Claude 與 Codex 版比較

比較日期：2026-08-04

## 比較範圍

| 類型 | Claude 版 | Codex 正式版 |
|---|---|---|
| 學生 notebook | `生成式AI應用開發_第10週_Embedding與語意搜尋_學生版_Claude生成.ipynb` | `生成式AI應用開發_第10週_Embedding與語意搜尋實作教材_學生版.ipynb` |
| 教師 notebook | `生成式AI應用開發_第10週_Embedding與語意搜尋_教師版_Claude生成.ipynb` | `生成式AI應用開發_第10週_Embedding與語意搜尋實作教材_教師版.ipynb` |
| Streamlit 專案 | `week10_semantic_search_claude/` | `week10_semantic_search_app/` |

## Notebook 結構比較

| 項目 | Claude 版 | Codex 正式版 | 教學判斷 |
|---|---|---|---|
| Cell 數量 | 學生/教師各 31 cells | 學生/教師各 34 cells | Codex 版多放 ChromaDB preview、App 對應與完成檢核 |
| Markdown cell type | 使用 `md` | 使用標準 `markdown` | Codex 版較符合 Jupyter/Colab 格式要求 |
| 學生 TODO | 16 個 | 8 個 | Codex 版減少 TODO 密度，避免學生在第一次接觸 embedding 時卡在太多實作缺口 |
| 教師 TODO | 0 個 | 0 個 | 兩者皆符合教師版完整答案原則 |
| 主線安排 | Embedding 概念、OpenAI API、語意搜尋、ChromaDB、FAISS | 第 9 週 chunking 銜接、本機假 embedding、cosine similarity、最小索引、OpenAI API、ChromaDB preview、ChromaDB/FAISS 選型 | Codex 版更明確把第 10 週定位為 retrieval，不提前混入第 11 週 RAG 生成 |
| 程式註解 | 有教學說明，但部分偏功能描述 | 全部採繁體中文，補上參數、回傳、錯誤與教學重點 | Codex 版符合目前教材註解規範 |

## Streamlit 專案比較

| 項目 | Claude 版 `week10_semantic_search_claude/` | Codex 正式版 `week10_semantic_search_app/` |
|---|---|---|
| 主索引設計 | ChromaDB-first，以 collection 作為主要檢索介面 | `list[dict]` + NumPy-first，以最小索引呈現資料流 |
| ChromaDB | 主流程依賴 | Notebook 有可執行 preview，App 有選讀 helper；不列為正式 app 必要依賴 |
| FAISS | 概念比較 | 概念比較，不在 Week10 要求安裝 |
| 離線模式 | 有假 embedding，可無 API key 展示流程 | 有假 embedding，並明確標示僅供流程測試、不代表真語意 |
| OpenAI Embeddings | 可切換真實 embedding | 可切換真實 embedding，預設 `text-embedding-3-small` |
| 文件處理 | 支援常見格式，銜接第 9 週 | 支援 PDF、DOCX、CSV、TXT、MD，並保留來源與位置 metadata |
| 教室穩定性 | ChromaDB 依賴較重，Windows/部署環境變數較多 | 依賴較輕，較適合作為全班共同起點 |

## Codex 版吸收了 Claude 版哪些優點

- 保留離線假 embedding，讓學生不需要 API key 也能跑完整流程。
- 保留 ChromaDB 與 FAISS 的比較，並加入 ChromaDB preview；但不讓套件安裝變成本週主要障礙。
- 保留可上傳文件並搜尋 top-k 結果的 Streamlit 專案方向。
- 保留從 notebook 到 app 的橋接，讓學生能看出練習函式如何進入實際專案。

## Codex 版刻意調整的地方

- 不把 ChromaDB 作為第 10 週正式 app 的必要依賴。第 10 週重點仍是讓學生看懂 embedding、index、query embedding、similarity 與 result sorting。
- 將 ChromaDB 放到 `embedding_utils.py` 的選讀 helper，方便第 11 週 RAG 或進階學生延伸。
- 在 notebook 增加 ChromaDB preview cell，示範 `EphemeralClient()`、`collection.add()` 與 `collection.query()`，但未把它改成全班必跑主線。
- 不在第 10 週直接做生成式回答，避免 retrieval 與 RAG answer generation 混在一起。
- notebook 使用標準 `markdown` cell type，避免後續 Colab 或 Jupyter 工具鏈相容性問題。
- 學生版 TODO 數量收斂到三個主要練習與一個 app checklist，讓教學重點集中在 metadata、門檻與 RAG context 前置整理。

## 建議採用結論

正式第 10 週教材建議採 Codex 版作為主線，Claude 版保留為參考資料。

理由是 Codex 版較符合目前課程路線：先用最小可觀察資料結構建立心智模型，再用 ChromaDB preview 讓學生看見向量資料庫如何保存 documents、embeddings 與 metadata，最後把 ChromaDB/FAISS 視為資料量、持久化與效能需求出現後的工具選項。這樣能降低環境安裝風險，也能讓第 11 週 RAG 更自然接上來源引用與 context 組裝。

Claude 版較適合作為進階補充：當班級已經能穩定操作 embedding 與 retrieval 後，可示範 ChromaDB 如何把向量、文字與 metadata 放在同一個 collection 裡管理。

## 後續修訂建議

- 第 10 週上課前，實際使用 `week10/week10_semantic_search_app/sample_data/ai_course_faq.md` 跑一次離線搜尋流程。
- 若課程時間足夠，可在教師補充中執行 notebook 的 ChromaDB preview 或 app helper `build_chroma_collection()`，但不要求學生每台機器都安裝 ChromaDB。
- 第 11 週教材應直接接續 Codex 版 `build_rag_context()`，要求回答必須保留來源 chunk。
