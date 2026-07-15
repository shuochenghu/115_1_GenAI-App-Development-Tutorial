import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

# 頁面設定要放在其他 Streamlit 畫面元件之前。
st.set_page_config(page_title="Week 7 AI App", page_icon="🤖", layout="centered")


def get_secret(name, default=None):
    """先讀 Streamlit Secrets；本機開發時再改讀 .env。"""
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        # 本機直接執行時可能沒有 st.secrets，改用 .env 即可。
        pass
    load_dotenv()
    return os.getenv(name, default)


def create_client():
    """建立 OpenAI client，並在缺少 API key 時給出明確錯誤。"""
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("找不到 OPENAI_API_KEY，請設定 .env 或 Streamlit Secrets。")
    return OpenAI(api_key=api_key)


def ask_ai(user_input, system_prompt="你是有幫助的 AI 助理。"):
    """非串流版本：適合摘要、分類等一次性任務。"""
    client = create_client()
    model = get_secret("OPENAI_MODEL", "gpt-5.4-mini")
    response = client.responses.create(
        model=model,
        instructions=system_prompt,
        input=user_input,
    )
    return response.output_text


def stream_ai(user_input, system_prompt="你是有幫助的 AI 助理。"):
    """串流版本：逐段 yield 文字，交給 st.write_stream() 顯示。"""
    client = create_client()
    model = get_secret("OPENAI_MODEL", "gpt-5.4-mini")
    stream = client.responses.create(
        model=model,
        instructions=system_prompt,
        input=user_input,
        stream=True,
    )
    for event in stream:
        # Responses API streaming 會送出多種事件；這裡只取文字 delta。
        if getattr(event, "type", None) == "response.output_text.delta":
            yield event.delta


def init_messages():
    """初始化聊天紀錄；Streamlit rerun 後仍會保留 session_state。"""
    if "messages" not in st.session_state:
        st.session_state.messages = []


def add_message(role, content):
    """把一則訊息加入聊天紀錄，role 通常是 user 或 assistant。"""
    st.session_state.messages.append({"role": role, "content": content})


def reset_messages():
    """清空聊天紀錄，搭配 st.rerun() 讓畫面立即更新。"""
    st.session_state.messages = []


st.title("Week 7 Streamlit AI App")
st.caption("OpenAI Responses API + Streamlit streaming + session state")

# Sidebar 放全域設定，不佔用主要互動畫面。
with st.sidebar:
    st.header("設定")
    system_prompt = st.text_area("System prompt", value="你是有幫助的 AI 助理。")
    use_streaming = st.toggle("使用串流回覆", value=True)
    if st.button("清空聊天紀錄"):
        reset_messages()
        st.rerun()

# 不顯示 key 內容，只提醒是否已設定。
if not get_secret("OPENAI_API_KEY"):
    st.warning("尚未設定 OPENAI_API_KEY。請建立 .env 或在 Streamlit Secrets 中設定。")

# 用 tabs 把聊天、摘要、檔案工具分開，避免單頁內容過長。
tab_chat, tab_summary, tab_file = st.tabs(["聊天", "摘要", "檔案"])

with tab_chat:
    init_messages()

    # 每次 rerun 都先重畫歷史訊息。
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input("請輸入問題")
    if prompt:
        add_message("user", prompt)
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            if use_streaming:
                answer = st.write_stream(stream_ai(prompt, system_prompt))
            else:
                answer = ask_ai(prompt, system_prompt)
                st.write(answer)
        add_message("assistant", answer)

with tab_summary:
    # 表單適合固定任務：使用者填完欄位後再一次送出。
    with st.form("summary_form"):
        source_text = st.text_area("貼上要摘要的文字", height=180)
        style = st.selectbox("摘要風格", ["條列重點", "一段式摘要", "給主管看的摘要"])
        submitted = st.form_submit_button("產生摘要")
    if submitted and source_text:
        prompt = f"請將以下內容整理成{style}：\n\n{source_text}"
        st.subheader("摘要結果")
        st.write(ask_ai(prompt, system_prompt="你是嚴謹的摘要助理。"))

with tab_file:
    # 第 7 週先處理純文字檔；PDF / Word / CSV 會在後續文件處理週延伸。
    uploaded_file = st.file_uploader("上傳 .txt 或 .md 檔案", type=["txt", "md"])
    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8")
        st.text_area("檔案內容預覽", text[:2000], height=200)
        if st.button("摘要這份檔案"):
            # 控制輸入長度，避免單次測試成本過高。
            prompt = "請摘要以下文字，列出 5 個重點：\n\n" + text[:12000]
            st.write(ask_ai(prompt, system_prompt="你是文件摘要助理。"))