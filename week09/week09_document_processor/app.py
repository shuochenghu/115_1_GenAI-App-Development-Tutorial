"""第 9 週 Streamlit 文件處理與摘要示範 App。

這個檔案刻意把「本機文件前處理」和「付費 AI 摘要」分成兩段：
學生可以先確認檔案抽取、清理與 chunking 都正確，再理解何時才需要呼叫 API。
"""

from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

from document_utils import SUPPORTED_EXTENSIONS, chunk_text, clean_text, extract_text


st.set_page_config(page_title="Week 9 文件處理工具", page_icon="📄", layout="wide")

# 這兩個上限是課堂示範用的安全護欄：
# - MAX_FILE_BYTES 對齊 .streamlit/config.toml，避免大檔拖慢本機與雲端環境。
# - MAX_AI_INPUT_CHARS 控制送進模型的文字長度，讓成本與延遲更容易預估。
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_AI_INPUT_CHARS = 12000
SYSTEM_PROMPT = (
    "你是嚴謹的文件整理助理。只能根據使用者提供的文件內容整理；"
    "若擷取文字可能不完整，必須明確說明，不得補寫文件中沒有的事實。"
)


def get_secret(name: str, default: str | None = None) -> str | None:
    """讀取設定值，優先使用 Streamlit Secrets，再退回本機環境變數。

    教學重點：
    1. 部署到 Streamlit Community Cloud 時，金鑰通常放在 `st.secrets`。
    2. 本機開發時，學生常用 `.env` 或作業系統環境變數。
    3. 函式只回傳設定值，不在畫面或 log 中印出秘密，避免外洩。
    """
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        # 在一般 Python 測試或 secrets 尚未建立時，讀取 st.secrets 可能失敗；
        # 這裡安靜退回環境變數，讓學生能先完成本機流程。
        pass
    load_dotenv()
    return os.getenv(name, default)


def summarize_document(text: str) -> str:
    """在使用者明確按下按鈕後，才呼叫 Responses API 產生文件摘要。

    參數：
        text: 已完成抽取、清理的文件文字；這裡不再負責讀檔或切塊。

    回傳：
        模型回傳的繁體中文摘要文字。

    可能錯誤：
        RuntimeError: 找不到 API key，或模型沒有回傳可顯示的文字。
    """
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("找不到 OPENAI_API_KEY，請先設定 `.env` 或 Streamlit Secrets。")

    # OpenAI client 在按鈕事件內才建立，避免使用者只預覽文件時就初始化付費流程。
    client = OpenAI(api_key=api_key)
    model = get_secret("OPENAI_MODEL", "gpt-5.4-mini")
    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=(
            # 只送出前 MAX_AI_INPUT_CHARS 字，讓課堂示範有可控的成本上限。
            "請用繁體中文輸出：\n"
            "1. 兩到四句摘要\n2. 五個重點\n3. 文件資料限制或擷取風險\n\n"
            f"文件內容：\n{text[:MAX_AI_INPUT_CHARS]}"
        ),
    )
    if not response.output_text:
        raise RuntimeError("AI 沒有回傳文字結果。")
    return response.output_text


def render_sidebar() -> tuple[int, int]:
    """集中渲染側欄控制項，並回傳 chunking 需要的兩個參數。

    側欄刻意放「切塊參數」和「安全提醒」，讓學生看到：
    - UI 控制值會影響後續純函式 `chunk_text()` 的輸出。
    - 上傳與前處理是本機流程，不等於自動把文件送到 AI。
    """
    with st.sidebar:
        st.header("Chunking 設定")
        # chunk_size 越大，單段內容越完整，但後續模型輸入成本也越高。
        chunk_size = st.slider("chunk_size（字元）", 200, 2000, 800, 100)
        # overlap 保留段落交界處的上下文；必須小於 chunk_size，否則切塊會無法前進。
        overlap = st.slider("overlap（字元）", 0, min(400, chunk_size - 1), 120, 20)
        st.divider()
        st.markdown("**處理管線**")
        st.markdown("上傳 → 抽取 → 清理 → chunking → 預覽 → 選擇性 AI 摘要")
        st.info("上傳、抽取、清理與切塊都在本機完成，不會自動呼叫 AI。")
        st.error("不要上傳機密、個資或未授權文件；API key 不可寫入程式碼。")
    return chunk_size, overlap


def main() -> None:
    """渲染完整文件處理流程：上傳、抽取、清理、切塊、預覽、匯出與選擇性摘要。

    Streamlit 每次互動都會重新執行整個檔案，因此昂貴或付費的動作要放在
    明確的按鈕條件內；一般上傳、清理與預覽則保持可重跑、可觀察。
    """
    st.title("📄 Week 9 文件處理與資料前處理")
    st.caption("PDF／Word／CSV／文字讀取 → 清理 → chunking → 預覽 → 選擇性 AI 摘要")

    chunk_size, overlap = render_sidebar()

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
        # 本機前處理三步驟：
        # 1. 依副檔名選 reader 抽文字。
        # 2. 清理換行與空白，讓後續切塊穩定。
        # 3. 依側欄設定建立 chunks，供預覽、匯出與 AI 摘要使用。
        raw_text = extract_text(uploaded.name, uploaded.getvalue())
        cleaned_text = clean_text(raw_text)
        chunks = chunk_text(cleaned_text, chunk_size=chunk_size, overlap=overlap)
    except (ValueError, UnicodeError) as exc:
        # 預期內錯誤通常代表檔案格式、編碼或內容不適合本週 reader。
        st.error(str(exc))
        return
    except Exception as exc:
        # 未預期錯誤保留原始訊息，方便教師示範如何回報與除錯。
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
        # 匯出 JSON 是第 10 週 embedding / RAG 的銜接點：
        # chunks 先被保存成結構化資料，下一週才能進一步轉成向量索引。
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
            # 這個按鈕是付費 API 的唯一觸發點，避免 Streamlit rerun 重複扣款。
            with st.spinner("正在整理文件..."):
                st.markdown(summarize_document(cleaned_text))
        except RuntimeError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"API 呼叫失敗：{exc}")


if __name__ == "__main__":
    main()
