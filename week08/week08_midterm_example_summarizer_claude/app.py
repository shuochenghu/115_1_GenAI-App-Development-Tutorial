"""
Week 8 期中專題 — 教師 demo 完整範例：AI 摘要器（Claude 版）

這是一個「完成度參考」：完全可執行，示範一個期中專題該長什麼樣。
學生不可直接繳交本範例；你的專題必須有自己的題目、prompt、欄位與 README。

示範重點：
1. 結構化輸出用 Pydantic（第 6 週）：responses.parse() + output_parsed。
2. 兩種輸入來源：貼上文字 或 上傳 .txt / .md 檔。
3. 加分項目：streaming 一段式摘要、成本/隱私提醒。
4. 安全與健壯性：API key 缺失提示、輸入驗證、輸入長度上限、錯誤處理。

helper 命名對齊第 7 週課堂版本（Codex 版 week07_streamlit_app）。
"""

import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
import streamlit as st


st.set_page_config(page_title="AI 摘要器（範例）", page_icon="📝", layout="centered")

MAX_INPUT_CHARS = 12000


# ─────────────────────────────────────────────────────────────
# 結構化輸出欄位（Pydantic）
# ─────────────────────────────────────────────────────────────
class SummaryResult(BaseModel):
    """一份文件摘要的結構化結果。"""

    title: str = Field(description="替這份文件下一個貼切的短標題")
    summary: str = Field(description="用 3 到 4 句話說明整份文件的重點")
    key_points: list[str] = Field(description="條列 3 到 6 個重點")
    keywords: list[str] = Field(description="3 到 8 個關鍵字")
    action_items: list[str] = Field(description="從內容整理出的待辦事項；若無則回傳空陣列")


SUMMARY_SYSTEM_PROMPT = (
    "你是嚴謹的中文摘要助理。請只根據使用者提供的內容摘要，"
    "不要加入原文沒有的資訊；若內容不足以判斷，請在摘要中誠實說明。"
)


# ─────────────────────────────────────────────────────────────
# helper（對齊第 7 週 week07_streamlit_app）
# ─────────────────────────────────────────────────────────────
def get_secret(name, default=None):
    """先讀 Streamlit Secrets（雲端），本機再改讀 .env。"""
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    load_dotenv()
    return os.getenv(name, default)


def create_client():
    """建立 OpenAI client，缺 API key 時 fail-fast。"""
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("找不到 OPENAI_API_KEY，請設定 .env 或 Streamlit Secrets。")
    return OpenAI(api_key=api_key)


def summarize_structured(source_text):
    """回傳 SummaryResult：程式可穩定取欄位的結構化摘要。"""
    client = create_client()
    model = get_secret("OPENAI_MODEL", "gpt-5.4-mini")
    response = client.responses.parse(
        model=model,
        instructions=SUMMARY_SYSTEM_PROMPT,
        input=f"請摘要以下文件：\n\n{source_text}",
        text_format=SummaryResult,
    )
    result = response.output_parsed
    if result is None:
        raise RuntimeError("AI 沒有回傳可解析的摘要結果，請稍後再試。")
    return result


def stream_ai(user_input, system_prompt=SUMMARY_SYSTEM_PROMPT):
    """串流一段式摘要（加分項）：逐段 yield，交給 st.write_stream()。"""
    client = create_client()
    model = get_secret("OPENAI_MODEL", "gpt-5.4-mini")
    stream = client.responses.create(
        model=model,
        instructions=system_prompt,
        input=user_input,
        stream=True,
    )
    for event in stream:
        if getattr(event, "type", None) == "response.output_text.delta":
            yield event.delta


# ─────────────────────────────────────────────────────────────
# 畫面
# ─────────────────────────────────────────────────────────────
def read_source_text():
    """從「貼上文字」或「上傳檔案」取得要摘要的內容。"""
    tab_text, tab_file = st.tabs(["貼上文字", "上傳檔案"])

    with tab_text:
        pasted = st.text_area("貼上要摘要的文字", height=220)

    with tab_file:
        uploaded = st.file_uploader("上傳 .txt 或 .md 檔", type=["txt", "md"])
        file_text = ""
        if uploaded is not None:
            file_text = uploaded.read().decode("utf-8", errors="ignore")
            st.text_area("檔案內容預覽", file_text[:2000], height=160, disabled=True)

    # 檔案優先；沒有檔案才用貼上的文字。
    return (file_text or pasted).strip()


def render_summary(result):
    """把結構化摘要顯示成好讀的區塊。"""
    st.subheader(result.title)
    st.write(result.summary)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 重點")
        for item in result.key_points:
            st.markdown(f"- {item}")
    with col2:
        st.markdown("#### 待辦事項")
        if result.action_items:
            for item in result.action_items:
                st.markdown(f"- {item}")
        else:
            st.caption("（內容中沒有明確待辦事項）")

    st.markdown("#### 關鍵字")
    st.write("　".join(f"`{kw}`" for kw in result.keywords))

    with st.expander("查看原始 JSON"):
        st.json(result.model_dump())


def main():
    st.title("📝 AI 摘要器（教師 demo 範例）")
    st.caption("貼上長文或上傳文字檔，產生結構化摘要（標題、重點、關鍵字、待辦）。")

    with st.sidebar:
        st.header("關於這個範例")
        st.markdown(
            "- 結構化輸出：Pydantic + `responses.parse()`\n"
            "- 輸入：貼上文字 或 上傳 .txt / .md\n"
            "- 加分：一段式串流摘要"
        )
        st.divider()
        st.caption("提醒：勿上傳含個資或機密的文件；AI 摘要可能有誤，請人工複核。")
        st.error("紅線：API key 只能放 .env 或 Secrets，絕不可寫死或推上 GitHub。")

    if not get_secret("OPENAI_API_KEY"):
        st.warning("尚未設定 OPENAI_API_KEY。請建立 `.env` 或在 Streamlit Secrets 中設定。")

    source_text = read_source_text()
    use_stream = st.toggle("同時顯示一段式串流摘要（加分示範）", value=False)
    run = st.button("產生摘要", type="primary")

    if not run:
        return

    if not source_text:
        st.error("請先貼上文字或上傳檔案。")
        return
    if len(source_text) > MAX_INPUT_CHARS:
        st.error(f"輸入過長（{len(source_text)} 字），請縮短到 {MAX_INPUT_CHARS} 字以內。")
        return

    try:
        with st.spinner("AI 正在摘要中..."):
            result = summarize_structured(source_text)
        render_summary(result)

        if use_stream:
            st.divider()
            st.markdown("#### 一段式摘要（串流）")
            st.write_stream(
                stream_ai(f"請用一段約 100 字的中文摘要以下文件：\n\n{source_text}")
            )
    except RuntimeError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"執行時發生未預期錯誤：{exc}")


if __name__ == "__main__":
    main()
