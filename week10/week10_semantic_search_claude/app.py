"""第 10 週｜文件語意搜尋 Streamlit App（Claude 版）。

流程：上傳文件 → 本機 chunk（第 9 週管線）→ 產生 embedding → 建 ChromaDB 索引
     → 輸入問題 → 找出最相近的 top-k 片段（顯示來源與相似度）。

完整 RAG 問答與生成式回答留到第 11 週；本週只做「找到相關片段」。
"""

from __future__ import annotations

from document_utils import SUPPORTED_EXTENSIONS, chunk_text, clean_text, extract_text
from embedding_utils import build_chroma_collection, query_chroma
import streamlit as st


st.set_page_config(page_title="Week 10 文件語意搜尋", page_icon="🔎", layout="wide")

MAX_FILE_BYTES = 8 * 1024 * 1024


def render_sidebar() -> tuple[int, int, int, bool]:
    """側邊欄設定；回傳 (chunk_size, overlap, top_k, offline_mode)。"""
    with st.sidebar:
        st.header("⚙️ 設定")
        chunk_size = st.slider("chunk_size（字元）", 200, 2000, 800, 100)
        overlap = st.slider("overlap（字元）", 0, min(400, chunk_size - 1), 120, 20)
        top_k = st.slider("top_k（回傳片段數）", 1, 10, 5, 1)
        st.divider()
        offline_mode = st.checkbox(
            "離線示範模式（假 embedding）",
            value=False,
            help="不需 API key，可驗證搜尋管線，但沒有真正語意。取消勾選才是真語意搜尋。",
        )
        if offline_mode:
            st.warning("目前是離線假 embedding，只驗證流程；語意效果需真 API。")
        st.divider()
        st.info("建立索引與查詢都在本機組裝；只有真語意模式會呼叫付費 Embeddings API。")
        st.error("不要上傳機密或個資文件；API key 不可寫入程式碼。")
    return chunk_size, overlap, top_k, offline_mode


def build_index(file_bytes: bytes, filename: str, chunk_size: int, overlap: int, offline: bool):
    """讀檔 → 清理 → chunk → 建 ChromaDB collection，回傳 (collection, chunks)。"""
    raw_text = extract_text(filename, file_bytes)
    cleaned = clean_text(raw_text)
    chunks = chunk_text(cleaned, chunk_size=chunk_size, overlap=overlap)
    for chunk in chunks:
        chunk["source"] = filename
    collection = build_chroma_collection(chunks, offline=offline)
    return collection, chunks


def main() -> None:
    st.title("🔎 Week 10 文件語意搜尋")
    st.caption("上傳文件 → chunk → embedding → ChromaDB 索引 → 找出最相近的片段")

    chunk_size, overlap, top_k, offline_mode = render_sidebar()

    uploaded = st.file_uploader(
        "上傳 PDF、DOCX、CSV、TXT 或 MD",
        type=list(SUPPORTED_EXTENSIONS),
    )
    if uploaded is None:
        st.markdown(
            "先上傳一份**不含敏感資料**的文件。第 10 週只做語意搜尋（找相關片段），"
            "生成式問答與來源引用留到第 11 週 RAG。"
        )
        return

    if uploaded.size > MAX_FILE_BYTES:
        st.error(f"檔案超過 {MAX_FILE_BYTES // (1024 * 1024)} MB，請縮小後再試。")
        return

    # 只有在檔案或設定改變時才重建索引（重建才會呼叫 Embeddings API）。
    signature = (uploaded.name, uploaded.size, chunk_size, overlap, offline_mode)
    if st.session_state.get("index_signature") != signature:
        try:
            with st.spinner("建立向量索引中..."):
                collection, chunks = build_index(
                    uploaded.getvalue(), uploaded.name, chunk_size, overlap, offline_mode
                )
        except (ValueError, UnicodeError) as exc:
            st.error(str(exc))
            return
        except RuntimeError as exc:
            st.error(str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            st.error(f"建立索引失敗：{exc}")
            return
        st.session_state["collection"] = collection
        st.session_state["chunk_count"] = len(chunks)
        st.session_state["index_signature"] = signature

    st.success(f"索引就緒：{st.session_state['chunk_count']} 個 chunk"
               f"（{'離線假 embedding' if offline_mode else '真語意 embedding'}）")

    query = st.text_input("輸入你的問題或關鍵語句", placeholder="例如：這份文件的重點是什麼？")
    if st.button("搜尋", type="primary"):
        if not query.strip():
            st.warning("請先輸入查詢內容。")
            return
        try:
            with st.spinner("搜尋中..."):
                hits = query_chroma(
                    st.session_state["collection"], query, top_k=top_k, offline=offline_mode
                )
        except RuntimeError as exc:
            st.error(str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            st.error(f"搜尋失敗：{exc}")
            return

        if not hits:
            st.info("查無相近片段，試試換個說法或調整 top_k。")
            return

        st.subheader(f"最相近的 {len(hits)} 個片段")
        for rank, hit in enumerate(hits, start=1):
            meta = hit.get("metadata", {})
            source = meta.get("source", "")
            chunk_id = meta.get("chunk_id", "?")
            with st.expander(
                f"#{rank}｜相似度 {hit['score']}｜來源 {source} chunk {chunk_id}",
                expanded=(rank == 1),
            ):
                st.write(hit["text"])


if __name__ == "__main__":
    main()
