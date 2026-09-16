"""第 11 週 Streamlit RAG 文件問答 App。

資料流分成兩個明確操作：使用者按下索引按鈕後才處理文件與產生 embeddings；
使用者送出問題後才檢索並呼叫 Responses API。這兩個邊界可避免 Streamlit rerun
因一般 widget 變動重複觸發付費工作。
"""

from __future__ import annotations

import hashlib

from document_utils import SUPPORTED_EXTENSIONS, chunk_text, clean_text, extract_text
from embedding_utils import (
    DEFAULT_EMBEDDING_MODEL,
    build_chroma_index,
    get_secret,
    query_chroma_index,
)
from rag_utils import (
    DEFAULT_GENERATION_MODEL,
    INSUFFICIENT_EVIDENCE_MESSAGE,
    answer_from_hits,
    build_rag_context,
    format_sources,
)
import streamlit as st


st.set_page_config(page_title="Week 11 RAG 文件問答", page_icon="📚", layout="wide")

MAX_FILE_BYTES = 8 * 1024 * 1024


def initialize_state() -> None:
    """集中建立本頁會使用的 session state，避免 rerun 時讀到不存在的 key。"""
    st.session_state.setdefault("rag_index_signature", None)
    st.session_state.setdefault("rag_client", None)
    st.session_state.setdefault("rag_collection", None)
    st.session_state.setdefault("rag_chunks", [])
    st.session_state.setdefault("rag_cleaned_text", "")
    st.session_state.setdefault("rag_last_result", None)


def render_sidebar() -> tuple[int, int, int, float, int, bool, str, str]:
    """渲染會影響索引、檢索與生成成本的全域設定。"""
    with st.sidebar:
        st.header("RAG 設定")
        chunk_size = st.slider("chunk_size（字元）", 200, 2000, 800, 100)
        overlap = st.slider("overlap（字元）", 0, min(400, chunk_size - 1), 120, 20)
        top_k = st.slider("top_k（候選片段）", 1, 8, 4, 1)
        min_score = st.slider("最低相關分數", -1.0, 1.0, 0.20, 0.05)
        max_context_chars = st.slider("context 字元上限", 1000, 12000, 6000, 500)
        st.divider()

        retrieval_mode = st.segmented_control(
            "Embedding 模式",
            ["離線示範", "OpenAI Embeddings"],
            default="離線示範",
            required=True,
            width="stretch",
        )
        offline_mode = retrieval_mode == "離線示範"
        embedding_model = get_secret("OPENAI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
        generation_model = get_secret("OPENAI_MODEL", DEFAULT_GENERATION_MODEL)
        st.caption(f"Embedding：`{embedding_model}`")
        st.caption(f"Generation：`{generation_model}`")

        if offline_mode:
            st.info("離線向量可測試資料流，但不代表真正語意搜尋品質。")
        else:
            st.warning("建索引與每次查詢都會呼叫 Embeddings API。")
        st.warning("生成答案仍需 OpenAI API key，且只會在送出問題後執行。")
        st.error("不得上傳個資、機密或未授權文件；API key 不可寫入程式碼。")

    return (
        chunk_size,
        overlap,
        top_k,
        min_score,
        max_context_chars,
        offline_mode,
        embedding_model,
        generation_model,
    )


def make_index_signature(
    filename: str,
    file_bytes: bytes,
    *,
    chunk_size: int,
    overlap: int,
    offline: bool,
    embedding_model: str,
) -> tuple:
    """用檔案內容摘要與索引參數辨識舊索引是否仍可使用。"""
    content_digest = hashlib.sha256(file_bytes).hexdigest()
    return filename, content_digest, chunk_size, overlap, offline, embedding_model


def build_index_from_upload(
    filename: str,
    file_bytes: bytes,
    *,
    chunk_size: int,
    overlap: int,
    offline: bool,
    embedding_model: str,
):
    """執行讀檔、清理、chunking、embedding 與 ChromaDB 建索引。"""
    raw_text = extract_text(filename, file_bytes)
    cleaned_text = clean_text(raw_text)
    chunks = chunk_text(cleaned_text, chunk_size=chunk_size, overlap=overlap)
    for chunk in chunks:
        chunk["source"] = filename
    client, collection = build_chroma_index(
        chunks,
        offline=offline,
        model=embedding_model,
    )
    return cleaned_text, chunks, client, collection


def render_result(result: dict) -> None:
    """顯示答案、實際檢索來源、context 與基本引用檢查。"""
    if result.get("error"):
        st.error(result["error"])
        st.caption("檢索已完成；設定 API key 後可再次送出同一問題產生答案。")
    elif result.get("answer"):
        st.subheader("回答")
        st.markdown(result["answer"])

    st.subheader("來源")
    sources = result.get("sources", [])
    if not sources:
        st.info("沒有片段通過目前的相關分數門檻。")
    for source in sources:
        title = (
            f"{source['label']}｜{source['source']}｜"
            f"chunk {source['chunk_id']}｜分數 {source['score']}"
        )
        with st.expander(title, expanded=source["label"] == "來源 1"):
            st.caption(f"字元範圍：{source['range']}")
            st.write(source["text"])

    with st.expander("檢索 context 與基本評估"):
        st.text(result.get("context") or "沒有建立 context。")
        if result.get("evaluation"):
            st.json(result["evaluation"])


initialize_state()
(
    chunk_size,
    overlap,
    top_k,
    min_score,
    max_context_chars,
    offline_mode,
    embedding_model,
    generation_model,
) = render_sidebar()

st.title("Week 11 RAG 文件問答")
st.caption("ChromaDB 檢索、受限 context、文件依據回答與可核對來源")

# 元件明訂上限，讓不同啟動目錄的上傳限制一致；下方仍檢查收到的檔案。
uploaded = st.file_uploader(
    "上傳 PDF、DOCX、CSV、TXT 或 MD",
    type=list(SUPPORTED_EXTENSIONS),
    max_upload_size=MAX_FILE_BYTES // (1024 * 1024),
)
if uploaded is None:
    st.info("請上傳文件，或使用 `sample_data/course_handbook.md`。")
    st.stop()

if uploaded.size > MAX_FILE_BYTES:
    st.error(f"檔案超過 {MAX_FILE_BYTES // (1024 * 1024)} MB，請縮小後再試。")
    st.stop()

file_bytes = uploaded.getvalue()
current_signature = make_index_signature(
    uploaded.name,
    file_bytes,
    chunk_size=chunk_size,
    overlap=overlap,
    offline=offline_mode,
    embedding_model=embedding_model,
)
index_is_current = st.session_state["rag_index_signature"] == current_signature

with st.container(border=True):
    st.write(f"檔案：`{uploaded.name}`，大小：{uploaded.size / 1024:.1f} KB")
    build_clicked = st.button(
        "建立／更新索引",
        type="primary",
        icon=":material/database:",
        disabled=index_is_current,
    )

if build_clicked:
    try:
        with st.spinner("正在處理文件並建立 ChromaDB 索引..."):
            cleaned_text, chunks, client, collection = build_index_from_upload(
                uploaded.name,
                file_bytes,
                chunk_size=chunk_size,
                overlap=overlap,
                offline=offline_mode,
                embedding_model=embedding_model,
            )
    except (ValueError, UnicodeError, RuntimeError) as exc:
        st.error(str(exc))
        st.stop()
    except Exception as exc:
        st.error(f"建立索引失敗：{exc}")
        st.stop()

    # 只有整個建索引流程成功後才一起更新狀態，避免 UI 誤把半成品當成可用索引。
    st.session_state["rag_index_signature"] = current_signature
    st.session_state["rag_client"] = client
    st.session_state["rag_collection"] = collection
    st.session_state["rag_chunks"] = chunks
    st.session_state["rag_cleaned_text"] = cleaned_text
    st.session_state["rag_last_result"] = None
    st.rerun()

if not index_is_current or st.session_state["rag_collection"] is None:
    st.info("目前設定尚未建立索引；請按下「建立／更新索引」。")
    st.stop()

chunks = st.session_state["rag_chunks"]
metric_a, metric_b, metric_c = st.columns(3)
metric_a.metric("清理後字元數", len(st.session_state["rag_cleaned_text"]))
metric_b.metric("Chunk 數", len(chunks))
metric_c.metric("Embedding", "離線示範" if offline_mode else "OpenAI")

preview_tab, question_tab = st.tabs(["索引預覽", "文件問答"])

with preview_tab:
    selected_chunk = st.number_input(
        "Chunk 編號",
        min_value=0,
        max_value=len(chunks) - 1,
        value=0,
        step=1,
    )
    chunk = chunks[int(selected_chunk)]
    st.caption(f"來源={chunk.get('source')}｜範圍={chunk['start']}:{chunk['end']}")
    st.text_area("Chunk 文字", chunk["text"], height=260, disabled=True)

with question_tab:
    with st.form("rag_question_form", border=False):
        question = st.text_input(
            "問題",
            placeholder="例如：第 11 週的成果與安全要求是什麼？",
        )
        submitted = st.form_submit_button(
            "根據文件回答",
            type="primary",
            icon=":material/search:",
        )

    if submitted:
        try:
            hits = query_chroma_index(
                st.session_state["rag_collection"],
                question,
                top_k=top_k,
                min_score=min_score,
                offline=offline_mode,
                model=embedding_model,
            )
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))
            st.stop()
        except Exception as exc:
            st.error(f"檢索失敗：{exc}")
            st.stop()

        if not hits:
            result = {
                "answer": INSUFFICIENT_EVIDENCE_MESSAGE,
                "context": "",
                "sources": [],
                "evaluation": {
                    "used_refusal_message": True,
                    "passes_basic_check": True,
                },
            }
        else:
            try:
                with st.spinner("正在根據檢索片段產生回答..."):
                    result = answer_from_hits(
                        question,
                        hits,
                        max_context_chars=max_context_chars,
                        model=generation_model,
                    )
            except RuntimeError as exc:
                # 即使缺少金鑰或生成 API 失敗，仍保留檢索來源，方便學生分層除錯。
                result = {
                    "answer": None,
                    "error": str(exc),
                    "context": build_rag_context(hits, max_chars=max_context_chars),
                    "sources": format_sources(hits),
                    "evaluation": {},
                }
        st.session_state["rag_last_result"] = result

    if st.session_state["rag_last_result"] is not None:
        render_result(st.session_state["rag_last_result"])
