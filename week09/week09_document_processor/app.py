"""Week 9 Streamlit document processing and summarization app."""

from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

from document_utils import SUPPORTED_EXTENSIONS, chunk_text, clean_text, extract_text


st.set_page_config(page_title="Week 9 文件處理工具", layout="wide")

MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_AI_INPUT_CHARS = 12000
SYSTEM_PROMPT = (
    "你是嚴謹的文件整理助理。只能根據使用者提供的文件內容整理；"
    "若擷取文字可能不完整，必須明確說明，不得補寫文件中沒有的事實。"
)


def get_secret(name: str, default: str | None = None) -> str | None:
    """Read a setting from Streamlit Secrets first, then local environment."""
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    load_dotenv()
    return os.getenv(name, default)


def summarize_document(text: str) -> str:
    """Call the Responses API only after the user explicitly requests a summary."""
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("找不到 OPENAI_API_KEY，請先設定 `.env` 或 Streamlit Secrets。")

    client = OpenAI(api_key=api_key)
    model = get_secret("OPENAI_MODEL", "gpt-5.4-mini")
    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=(
            "請用繁體中文輸出：\n"
            "1. 兩到四句摘要\n2. 五個重點\n3. 文件資料限制或擷取風險\n\n"
            f"文件內容：\n{text[:MAX_AI_INPUT_CHARS]}"
        ),
    )
    if not response.output_text:
        raise RuntimeError("AI 沒有回傳文字結果。")
    return response.output_text


def main() -> None:
    """Render upload, local preprocessing, preview, export, and optional AI summary."""
    st.title("📄 Week 9 文件處理與資料前處理")
    st.caption("PDF／Word／CSV／文字讀取 → 清理 → chunking → 預覽 → 選擇性 AI 摘要")

    with st.sidebar:
        st.header("Chunking 設定")
        chunk_size = st.slider("chunk_size（字元）", 200, 2000, 800, 100)
        overlap = st.slider("overlap（字元）", 0, min(400, chunk_size - 1), 120, 20)
        st.divider()
        st.info("上傳、抽取、清理與切塊都在本機完成，不會自動呼叫 AI。")
        st.error("不要上傳機密、個資或未授權文件；API key 不可寫入程式碼。")

    uploaded = st.file_uploader(
        "上傳 PDF、DOCX、CSV、TXT 或 MD",
        type=list(SUPPORTED_EXTENSIONS),
    )
    if uploaded is None:
        st.markdown(
            "先選擇不含敏感資料的測試文件。PDF 必須具有文字層；掃描 PDF 需要 OCR，"
            "不在本週基礎範圍。"
        )
        return

    if uploaded.size > MAX_FILE_BYTES:
        st.error(f"檔案超過 {MAX_FILE_BYTES // (1024 * 1024)} MB，請縮小後再試。")
        return

    try:
        raw_text = extract_text(uploaded.name, uploaded.getvalue())
        cleaned_text = clean_text(raw_text)
        chunks = chunk_text(cleaned_text, chunk_size=chunk_size, overlap=overlap)
    except (ValueError, UnicodeError) as exc:
        st.error(str(exc))
        return
    except Exception as exc:
        st.error(f"文件處理失敗：{exc}")
        return

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("清理後字元數", len(cleaned_text))
    col_b.metric("Chunk 數", len(chunks))
    col_c.metric("檔案大小", f"{uploaded.size / 1024:.1f} KB")

    preview_tab, chunks_tab, export_tab = st.tabs(["文字預覽", "Chunks", "匯出"])
    with preview_tab:
        st.text_area("抽取與清理結果（前 8,000 字）", cleaned_text[:8000], height=420)

    with chunks_tab:
        if not chunks:
            st.warning("沒有可顯示的 chunk。")
        else:
            selected = st.number_input(
                "Chunk 編號",
                min_value=0,
                max_value=len(chunks) - 1,
                value=0,
                step=1,
            )
            chunk = chunks[int(selected)]
            st.caption(
                f"chunk_id={chunk['chunk_id']}｜範圍={chunk['start']}:{chunk['end']}｜"
                f"長度={len(chunk['text'])}"
            )
            st.text_area("Chunk 內容", chunk["text"], height=300)

    with export_tab:
        export_data = {
            "filename": uploaded.name,
            "character_count": len(cleaned_text),
            "chunk_size": chunk_size,
            "overlap": overlap,
            "chunks": chunks,
        }
        st.download_button(
            "下載 chunks JSON",
            data=json.dumps(export_data, ensure_ascii=False, indent=2),
            file_name=f"{uploaded.name}.chunks.json",
            mime="application/json",
        )

    st.divider()
    st.subheader("選擇性 AI 摘要")
    st.caption(
        f"只有按下按鈕才會呼叫 API；最多送出前 {MAX_AI_INPUT_CHARS:,} 字。"
    )
    if st.button("產生 AI 摘要", type="primary"):
        try:
            with st.spinner("正在整理文件..."):
                st.markdown(summarize_document(cleaned_text))
        except RuntimeError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"API 呼叫失敗：{exc}")


if __name__ == "__main__":
    main()
