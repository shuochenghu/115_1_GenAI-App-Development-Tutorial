"""
生成式AI應用開發 第 07 週 | Streamlit Web App 範例（Claude Code 產出）

這是課堂 notebook 一步步做出來的整合版，可直接部署到
Streamlit Community Cloud。功能：
  - 側邊欄設定 system prompt 與是否串流
  - 聊天分頁：session state 記憶 + 串流回覆 + 累計成本
  - 摘要分頁：st.form 表單，避免每次輸入就重跑
  - 檔案分頁：上傳 .txt / .md 做摘要

執行方式（本機）：
    pip install -r requirements.txt
    streamlit run app.py
"""

import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# --- 基本頁面設定 -----------------------------------------------------------
st.set_page_config(page_title="Week 7 AI App", page_icon="🤖", layout="centered")

# 預設模型；可用環境變數 / secrets 覆蓋
DEFAULT_MODEL = "gpt-5.4-mini"

# gpt-5.4-mini 的參考單價（美元 / 1K tokens），僅供課堂估算示範
PRICE_PER_1K_INPUT = 0.00015
PRICE_PER_1K_OUTPUT = 0.0006


def get_secret(name, default=None):
    """
    先讀 Streamlit Secrets（雲端部署用），
    找不到再讀本機 .env / 環境變數。
    """
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        # 本機沒有 secrets.toml 時，st.secrets 會丟例外，忽略即可
        pass
    load_dotenv()
    return os.getenv(name, default)


@st.cache_resource
def get_client():
    """建立 OpenAI client。用 cache_resource 避免每次互動都重建。"""
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def get_model():
    return get_secret("OPENAI_MODEL", DEFAULT_MODEL)


def ask_ai_safe(user_input, role="你是有幫助的 AI 助理，請用繁體中文回答。"):
    """單次問答；把錯誤包成友善訊息，不讓整個 App 崩潰。"""
    client = get_client()
    if client is None:
        return "⚠️ 尚未設定 OPENAI_API_KEY。"
    if not user_input or not user_input.strip():
        return "請先輸入內容。"
    try:
        response = client.responses.create(
            model=get_model(),
            instructions=role,
            input=user_input,
        )
        # 記錄 token 使用量，供成本估算
        _accumulate_usage(response)
        return response.output_text
    except Exception as e:
        return f"⚠️ 呼叫 API 時發生錯誤：{e}"


def stream_ai(user_input, role="你是有幫助的 AI 助理，請用繁體中文回答。"):
    """串流版本：逐字 yield，給 st.write_stream 使用。"""
    client = get_client()
    if client is None:
        yield "⚠️ 尚未設定 OPENAI_API_KEY。"
        return
    try:
        stream = client.responses.create(
            model=get_model(),
            instructions=role,
            input=user_input,
            stream=True,
        )
        for event in stream:
            if getattr(event, "type", None) == "response.output_text.delta":
                yield event.delta
            elif getattr(event, "type", None) == "response.completed":
                _accumulate_usage(event.response)
    except Exception as e:
        yield f"⚠️ 呼叫 API 時發生錯誤：{e}"


def _accumulate_usage(response):
    """把每次呼叫的 token 累加到 session_state，供成本估算。"""
    usage = getattr(response, "usage", None)
    if usage is None:
        return
    st.session_state.total_input = st.session_state.get("total_input", 0) + getattr(
        usage, "input_tokens", 0
    )
    st.session_state.total_output = st.session_state.get("total_output", 0) + getattr(
        usage, "output_tokens", 0
    )


def estimated_cost():
    ti = st.session_state.get("total_input", 0)
    to = st.session_state.get("total_output", 0)
    return ti / 1000 * PRICE_PER_1K_INPUT + to / 1000 * PRICE_PER_1K_OUTPUT


# --- 側邊欄 -----------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 設定")
    system_prompt = st.text_area(
        "System prompt（角色設定）",
        value="你是有幫助的 AI 助理，請用繁體中文回答。",
        height=120,
    )
    use_streaming = st.toggle("使用串流回覆", value=True)
    st.divider()
    st.caption("💰 本次累計用量")
    st.write(f"輸入 tokens：{st.session_state.get('total_input', 0)}")
    st.write(f"輸出 tokens：{st.session_state.get('total_output', 0)}")
    st.write(f"估計成本：約 US${estimated_cost():.5f}")
    if st.button("🗑️ 清空聊天與用量"):
        st.session_state.messages = []
        st.session_state.total_input = 0
        st.session_state.total_output = 0
        st.rerun()

# --- 主標題與金鑰提醒 -------------------------------------------------------
st.title("🤖 我的第一個 AI Web App")
st.caption("OpenAI Responses API + Streamlit（第 7 週範例）")

if get_secret("OPENAI_API_KEY") is None:
    st.warning("尚未偵測到 OPENAI_API_KEY，請建立 .env 或在 Streamlit Secrets 設定後重新整理。")

tab_chat, tab_summary, tab_file = st.tabs(["💬 聊天", "📝 摘要", "📄 檔案"])

# --- 分頁 1：聊天 -----------------------------------------------------------
with tab_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 先重畫過去的對話
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input("請輸入問題")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            if use_streaming:
                answer = st.write_stream(stream_ai(prompt, system_prompt))
            else:
                answer = ask_ai_safe(prompt, system_prompt)
                st.write(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

# --- 分頁 2：摘要表單 -------------------------------------------------------
with tab_summary:
    with st.form("summary_form"):
        source_text = st.text_area("貼上要摘要的文字", height=180)
        style = st.selectbox("摘要風格", ["條列重點", "一段式摘要", "給主管看的摘要"])
        submitted = st.form_submit_button("產生摘要")
    if submitted and source_text.strip():
        summary_prompt = f"請將以下內容整理成「{style}」：\n\n{source_text}"
        st.subheader("摘要結果")
        st.write(ask_ai_safe(summary_prompt, role="你是嚴謹的中文摘要助理。"))

# --- 分頁 3：檔案上傳 -------------------------------------------------------
with tab_file:
    uploaded_file = st.file_uploader("上傳 .txt 或 .md 檔案", type=["txt", "md"])
    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8", errors="ignore")
        st.text_area("檔案內容預覽", text[:2000], height=200)
        if st.button("摘要這份檔案"):
            file_prompt = "請閱讀以下文字並列出 5 個重點：\n\n" + text[:12000]
            st.write(ask_ai_safe(file_prompt, role="你是文件摘要助理。"))
