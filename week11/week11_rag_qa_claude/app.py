"""第 11 週｜文件問答（RAG）Streamlit App（Claude 版）。

流程：上傳文件 →（按按鈕才）建 ChromaDB 索引 → 提問 → 檢索 top-k
     → 組 context → 生成「只依文件、附來源引用」的答案。

設計重點：
- **索引只在按下「建立／更新索引」時才建**，避免調整 slider 時自動重建、
  在線上模式產生非預期的 Embeddings API 費用。
- 索引簽章使用**檔案內容雜湊**，避免同名同大小但內容不同的檔案沿用舊索引。
- 離線示範模式只做檢索與 context 預覽，不生成答案。

RAG helper（`build_rag_context` / `answer_from_hits` / `format_sources` 等）命名對齊
Codex 版 `week11_rag_app/`，兩版可互換對照。
"""

from __future__ import annotations

import hashlib

from document_utils import SUPPORTED_EXTENSIONS, chunk_text, clean_text, extract_text
from embedding_utils import build_chroma_collection, query_chroma
from rag_utils import (
    INSUFFICIENT_EVIDENCE_MESSAGE,
    answer_from_hits,
    build_rag_context,
    format_sources,
)
import streamlit as st


st.set_page_config(page_title="Week 11 文件問答 (RAG)", page_icon="💬", layout="wide")

MAX_FILE_BYTES = 8 * 1024 * 1024


def initialize_state() -> None:
    """集中建立本頁使用的 session state，避免 rerun 讀到不存在的 key。"""
    st.session_state.setdefault("rag_index_signature", None)
    st.session_state.setdefault("rag_collection", None)
    st.session_state.setdefault("rag_chunk_count", 0)
    st.session_state.setdefault("rag_last_result", None)


def render_sidebar() -> tuple[int, int, int, float, int, bool]:
    """側邊欄設定；回傳 (chunk_size, overlap, top_k, min_score, max_context_chars, offline)。"""
    with st.sidebar:
        st.header("⚙️ 設定")
        chunk_size = st.slider("chunk_size（字元）", 200, 2000, 800, 100)
        overlap = st.slider("overlap（字元）", 0, min(400, chunk_size - 1), 120, 20)
        top_k = st.slider("top_k（檢索片段數）", 1, 10, 4, 1)
        min_score = st.slider("最低相關分數（低於則不採用）", -1.0, 1.0, 0.20, 0.05)
        max_context_chars = st.slider("context 字元上限", 1000, 12000, 6000, 500)
        st.divider()
        offline_mode = st.checkbox(
            "離線示範模式（假 embedding，只檢索不生成）",
            value=False,
            help="不需 API key，可驗證檢索與 context 組裝；生成答案需真 API。",
        )
        if offline_mode:
            st.warning("離線模式只做檢索與 context 預覽，不會生成答案。")
        else:
            st.warning("線上模式：按下「建立／更新索引」與每次查詢都會呼叫 Embeddings API。")
        st.divider()
        st.info("答案只依據上傳文件；找不到會明確說找不到，並附上來源引用。")
        st.error("不要上傳機密或個資文件；API key 不可寫入程式碼。")
    return chunk_size, overlap, top_k, min_score, max_context_chars, offline_mode


def make_signature(filename: str, file_bytes: bytes, chunk_size: int, overlap: int, offline: bool) -> tuple:
    """用檔案**內容雜湊** + 索引參數辨識舊索引是否仍可用（避免同名同大小誤用舊索引）。"""
    content_digest = hashlib.sha256(file_bytes).hexdigest()
    return filename, content_digest, chunk_size, overlap, offline


def build_index(file_bytes: bytes, filename: str, chunk_size: int, overlap: int, offline: bool):
    """讀檔 → 清理 → chunk → 建 ChromaDB collection。"""
    raw_text = extract_text(filename, file_bytes)
    cleaned = clean_text(raw_text)
    chunks = chunk_text(cleaned, chunk_size=chunk_size, overlap=overlap)
    for chunk in chunks:
        chunk["source"] = filename
    collection = build_chroma_collection(chunks, offline=offline)
    return collection, len(chunks)


def render_sources(sources: list[dict]) -> None:
    """顯示引用來源與對應的原文片段（sources 來自 format_sources）。"""
    if not sources:
        st.info("沒有片段通過目前的相關分數門檻。")
        return
    for source in sources:
        title = f"{source['label']}｜{source['source']}｜chunk {source['chunk_id']}｜分數 {source['score']}"
        with st.expander(title, expanded=source["label"] == "來源 1"):
            st.caption(f"字元範圍：{source['range']}")
            st.write(source["text"])


def run_qa(question: str, top_k: int, min_score: float, max_context_chars: int, offline: bool) -> None:
    """檢索 → （線上）生成答案 / （離線）只預覽 context，並顯示來源。"""
    collection = st.session_state["rag_collection"]
    try:
        hits = query_chroma(collection, question, top_k=top_k, offline=offline, min_score=min_score)
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))
        return
    except Exception as exc:  # noqa: BLE001
        st.error(f"檢索失敗：{exc}")
        return

    if offline:
        st.info("（離線模式）以下為檢索到的參考資料，未生成答案；生成需真 API。")
        render_sources(format_sources(hits))
        with st.expander("組好的 context"):
            st.text(build_rag_context(hits, max_chars=max_context_chars) if hits else "沒有通過門檻的片段。")
        return

    try:
        with st.spinner("檢索並生成答案中..."):
            result = answer_from_hits(question, hits, max_context_chars=max_context_chars)
    except RuntimeError as exc:
        # 缺 key 或生成失敗時，仍保留檢索來源方便分層除錯。
        st.error(str(exc))
        st.caption("檢索已完成；設定 API key 後可再次送出同一問題產生答案。")
        render_sources(format_sources(hits))
        return
    except Exception as exc:  # noqa: BLE001
        st.error(f"問答失敗：{exc}")
        return

    st.subheader("答案")
    st.markdown(result["answer"])
    if result["answer"] == INSUFFICIENT_EVIDENCE_MESSAGE:
        st.caption("模型表示文件中找不到足夠依據。")
    st.divider()
    st.subheader("來源")
    render_sources(result["sources"])
    with st.expander("檢索 context 與基本評估"):
        st.text(result.get("context") or "沒有建立 context。")
        if result.get("evaluation"):
            st.json(result["evaluation"])


def main() -> None:
    initialize_state()
    st.title("💬 Week 11 文件問答 (RAG)")
    st.caption("上傳文件 → 建索引 → 檢索相關片段 → 生成只依文件、附來源引用的答案")

    chunk_size, overlap, top_k, min_score, max_context_chars, offline_mode = render_sidebar()

    uploaded = st.file_uploader(
        "上傳 PDF、DOCX、CSV、TXT 或 MD",
        type=list(SUPPORTED_EXTENSIONS),
    )
    if uploaded is None:
        st.markdown("先上傳一份**不含敏感資料**的文件，再建立索引與提問。")
        return

    if uploaded.size > MAX_FILE_BYTES:
        st.error(f"檔案超過 {MAX_FILE_BYTES // (1024 * 1024)} MB，請縮小後再試。")
        return

    file_bytes = uploaded.getvalue()
    signature = make_signature(uploaded.name, file_bytes, chunk_size, overlap, offline_mode)
    index_is_current = st.session_state["rag_index_signature"] == signature

    # 索引只在明確按下按鈕時才建立／更新；調整 slider 不會自動重建（避免非預期 API 費用）。
    with st.container(border=True):
        st.write(f"檔案：`{uploaded.name}`，大小：{uploaded.size / 1024:.1f} KB")
        if index_is_current:
            st.success(f"索引就緒：{st.session_state['rag_chunk_count']} 個 chunk"
                       f"（{'離線假 embedding' if offline_mode else '真語意 embedding'}）")
        else:
            st.warning("目前設定尚未建立索引（或設定已變更）；請按下方按鈕建立。")
        build_clicked = st.button("建立／更新索引", type="primary", disabled=index_is_current)

    if build_clicked:
        try:
            with st.spinner("建立向量索引中..."):
                collection, chunk_count = build_index(
                    file_bytes, uploaded.name, chunk_size, overlap, offline_mode
                )
        except (ValueError, UnicodeError, RuntimeError) as exc:
            st.error(str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            st.error(f"建立索引失敗：{exc}")
            return
        st.session_state["rag_collection"] = collection
        st.session_state["rag_chunk_count"] = chunk_count
        st.session_state["rag_index_signature"] = signature
        st.session_state["rag_last_result"] = None
        st.rerun()

    if not index_is_current or st.session_state["rag_collection"] is None:
        return

    question = st.text_input("輸入你的問題", placeholder="例如：這份文件對期末專題有什麼要求？")
    if st.button("問答", type="primary"):
        if not question.strip():
            st.warning("請先輸入問題。")
            return
        run_qa(question, top_k, min_score, max_context_chars, offline_mode)


if __name__ == "__main__":
    main()
