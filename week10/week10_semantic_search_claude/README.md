# Week 10 文件語意搜尋（Claude 版）

第 10 週 Streamlit 範例專案（Claude Code 產出）。承接第 9 週的文件處理管線，
把 chunks 轉成 embedding、建立 ChromaDB 向量索引，輸入問題後找出**最相近的文件片段**。

> 本週只做到「找到相關片段」；完整 RAG 生成式問答與來源引用留到第 11 週。
> 與 Codex 版 `week10_semantic_search_app/` 為平行比較版本，helper 命名一致。

## 功能

- 上傳 PDF、DOCX、CSV、TXT、MD，沿用第 9 週 `document_utils.py` 抽取與 chunking。
- 用 OpenAI Embeddings（`text-embedding-3-small`）產生向量。
- 以 ChromaDB 建立 in-memory 向量索引（cosine 距離）。
- 輸入問題做 top-k 語意搜尋，顯示相似度與來源（檔名、chunk_id）。
- **離線示範模式**：不需 API key 也能用「假 embedding」跑完整條管線、驗證流程。

## 安裝與執行

```bash
cd week10/week10_semantic_search_claude
pip install -r requirements.txt
streamlit run app.py
```

## API 設定

複製 `.env.example` 為 `.env`：

```text
OPENAI_API_KEY=你的測試用APIKey
OPENAI_EMBED_MODEL=text-embedding-3-small
```

部署時改用 Streamlit Secrets（見 `.streamlit/secrets.example.toml`）。
不得將 `.env`、`.streamlit/secrets.toml` 或真實 API key 推送到 GitHub。

## 檔案結構

| 檔案 | 內容 |
|---|---|
| `document_utils.py` | 第 9 週文件抽取、清理、chunking（本機、不花錢） |
| `embedding_utils.py` | `get_embedding` / `cosine_similarity` / `search_chunks` / `build_chroma_collection` / `query_chroma` / `local_demo_embed` |
| `app.py` | Streamlit UI：上傳、建索引、語意搜尋、結果顯示 |
| `sample_data/ai_course_faq.md` | 測試文件 |

## 離線假 embedding 說明

`local_demo_embed()` 用雜湊把文字攤成固定長度向量：相同文字→相同向量，
但**沒有真正語意**。它只用來驗證 cosine／搜尋／ChromaDB 的程式邏輯是否正確；
真正的語意搜尋效果，一定要取消「離線示範模式」、使用真 Embeddings API 才算數。

## 向量資料庫：ChromaDB vs FAISS

本專案用 **ChromaDB**（Windows 環境穩定，向量＋原文＋metadata 綁在一起，
天然支援第 11 週的來源引用）。FAISS 是更底層、更快的相似度索引，但只存向量、
需自行管理原文對照，且 Windows 安裝較不穩，列為自主學習補充。

## 建議測試

1. 上傳 `sample_data/ai_course_faq.md`。
2. 先勾選「離線示範模式」，確認索引可建立、搜尋有回傳（驗證流程）。
3. 取消離線模式並設定 API key，搜尋「語意搜尋和關鍵字差在哪」，觀察真語意效果。
4. 調整 `top_k` 與 `chunk_size`，比較回傳片段與相似度變化。
