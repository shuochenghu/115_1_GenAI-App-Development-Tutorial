"""第 10 週 Streamlit 文件語意搜尋 App。

本 App 承接第 9 週文件處理管線，示範如何把 chunks 轉成 embedding，
再用 cosine similarity 找出與查詢最相近的片段。完整 RAG 生成式回答留到第 11 週。
"""

from __future__ import annotations

from document_utils import SUPPORTED_EXTENSIONS, chunk_text, clean_text, extract_text
from embedding_utils import (
    DEFAULT_EMBEDDING_MODEL,
    build_embedding_index,
    get_secret,
    search_index,
)
import streamlit as st


st.set_page_config(page_title="Week 10 文件語意搜尋", page_icon="🔎", layout="wide")

MAX_FILE_BYTES = 8 * 1024 * 1024


def render_sidebar() -> tuple[int, int, int, bool, str]:
    """渲染側欄設定，集中管理會影響索引與查詢成本的參數。"""
    with st.sidebar:
        st.header("搜尋設定")
        chunk_size = st.slider("chunk_size（字元）", 200, 2000, 800, 100)
        overlap = st.slider("overlap（字元）", 0, min(400, chunk_size - 1), 120, 20)
        top_k = st.slider("top_k（回傳片段數）", 1, 10, 5, 1)
        st.divider()
        offline_mode = st.checkbox(
            "離線示範模式",
            value=True,
            help="使用本機假 embedding，不需要 API key；取消勾選才會呼叫 OpenAI Embeddings API。",
        )
        model = get_secret("OPENAI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
        st.caption(f"Embedding model：`{model}`")
        if offline_mode:
            st.info("離線模式只驗證搜尋管線，沒有真正語意。")
        else:
            st.warning("真語意模式會在建立索引與搜尋時呼叫付費 API。")
        st.error("不要上傳機密、個資或未授權文件；API key 不可寫入程式碼。")
    return chunk_size, overlap, top_k, offline_mode, model


def build_index_from_upload(
    filename: str,
    file_bytes: bytes,
    *,
    chunk_size: int,
    overlap: int,
    offline: bool,
    model: str,
) -> tuple[str, list[dict], list[dict]]:
    """讀檔、清理、chunking 並建立 embedding index。

    這個 helper 把昂貴流程集中起來，讓 Streamlit UI 只在使用者按下按鈕時執行。
    """
    raw_text = extract_text(filename, file_bytes)
    cleaned_text = clean_text(raw_text)
    chunks = chunk_text(cleaned_text, chunk_size=chunk_size, overlap=overlap)
    for chunk in chunks:
        chunk["source"] = filename
    indexed_chunks = build_embedding_index(chunks, offline=offline, model=model)
    return cleaned_text, chunks, indexed_chunks


chunk_size, overlap, top_k, offline_mode, model = render_sidebar()

st.title("🔎 Week 10 文件語意搜尋")
st.caption("上傳文件 → chunk → embedding → cosine similarity → 找出最相近片段")

uploaded = st.file_uploader("上傳 PDF、DOCX、CSV、TXT 或 MD", type=list(SUPPORTED_EXTENSIONS))
if uploaded is None:
    st.markdown(
        "請先上傳不含敏感資料的文件，或使用 `sample_data/ai_course_faq.md` 測試。"
        "本週只做 retrieval；第 11 週才把搜尋結果交給模型生成答案。"
    )
    st.stop()

if uploaded.size > MAX_FILE_BYTES:
    st.error(f"檔案超過 {MAX_FILE_BYTES // (1024 * 1024)} MB，請縮小後再試。")
    st.stop()

signature = (uploaded.name, uploaded.size, chunk_size, overlap, offline_mode, model)
needs_rebuild = st.session_state.get("index_signature") != signature

with st.container(border=True):
    st.write(f"檔案：`{uploaded.name}`，大小：{uploaded.size / 1024:.1f} KB")
    st.caption("只有按下「建立/更新索引」才會產生 embeddings；調整參數後需重新建立索引。")
    build_clicked = st.button(
        "建立/更新索引",
        type="primary",
        icon=":material/database:",
        disabled=not needs_rebuild and "indexed_chunks" in st.session_state,
    )

if build_clicked:
    try:
        with st.spinner("正在建立語意搜尋索引..."):
            cleaned_text, chunks, indexed_chunks = build_index_from_upload(
                uploaded.name,
                uploaded.getvalue(),
                chunk_size=chunk_size,
                overlap=overlap,
                offline=offline_mode,
                model=model,
            )
    except (ValueError, UnicodeError, RuntimeError) as exc:
        st.error(str(exc))
        st.stop()
    except Exception as exc:
        st.error(f"建立索引失敗：{exc}")
        st.stop()

    st.session_state["index_signature"] = signature
    st.session_state["cleaned_text"] = cleaned_text
    st.session_state["chunks"] = chunks
    st.session_state["indexed_chunks"] = indexed_chunks

if "indexed_chunks" not in st.session_state:
    st.info("索引尚未建立。請確認參數後按下「建立/更新索引」。")
    st.stop()

chunks = st.session_state["chunks"]
indexed_chunks = st.session_state["indexed_chunks"]

metric_a, metric_b, metric_c = st.columns(3)
metric_a.metric("清理後字元數", len(st.session_state["cleaned_text"]))
metric_b.metric("Chunk 數", len(chunks))
metric_c.metric("模式", "離線示範" if offline_mode else "OpenAI Embeddings")

preview_tab, search_tab = st.tabs(["索引預覽", "語意搜尋"])
with preview_tab:
    selected = st.number_input("Chunk 編號", min_value=0, max_value=len(chunks) - 1, value=0, step=1)
    chunk = chunks[int(selected)]
    st.caption(f"來源={chunk.get('source')}｜範圍={chunk['start']}:{chunk['end']}")
    st.text_area("Chunk 文字", chunk["text"], height=260)

with search_tab:
    with st.form("semantic_search_form"):
        query = st.text_input("輸入問題或查詢語句", placeholder="例如：第 10 週和第 11 週差在哪？")
        submitted = st.form_submit_button("搜尋", type="primary", icon=":material/search:")

    if submitted:
        try:
            hits = search_index(
                query,
                indexed_chunks,
                top_k=top_k,
                offline=offline_mode,
                model=model,
            )
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))
            st.stop()
        except Exception as exc:
            st.error(f"搜尋失敗：{exc}")
            st.stop()

        if not hits:
            st.info("沒有找到可顯示的結果。")
        else:
            for rank, hit in enumerate(hits, start=1):
                with st.expander(
                    f"#{rank}｜相似度 {hit['score']}｜chunk {hit['chunk_id']}",
                    expanded=(rank == 1),
                ):
                    st.caption(f"來源={hit.get('source')}｜範圍={hit.get('start')}:{hit.get('end')}")
                    st.write(hit["text"])
