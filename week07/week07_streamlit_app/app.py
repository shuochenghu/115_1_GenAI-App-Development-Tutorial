import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

# Streamlit 會從上到下執行整個檔案；頁面設定必須放在第一個畫面元件之前，
# 否則執行時可能出現「set_page_config 必須先呼叫」的錯誤。
st.set_page_config(page_title="Week 7 AI App", page_icon="🤖", layout="centered")


def get_secret(name, default=None):
    """
    讀取環境設定值，統一本機開發與部署環境的 API key 取得方式。

    教學重點：
    - 本機開發時，學生通常把 OPENAI_API_KEY 放在 `.env`。
    - 部署到 Streamlit Community Cloud 時，應改放在 Streamlit Secrets。
    - App 程式只呼叫這個函式，不需要到處判斷目前在哪個環境執行。

    Args:
        name: 要讀取的設定名稱，例如 OPENAI_API_KEY 或 OPENAI_MODEL。
        default: 找不到設定時要回傳的預設值。

    Returns:
        設定值字串；如果兩邊都找不到，回傳 default。
    """
    try:
        # 情況一：部署環境或本機有設定 Streamlit Secrets。
        # 注意：不要把 secret 印出來，只需要確認是否存在。
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        # 情況二：本機尚未建立 .streamlit/secrets.toml。
        # 這不是程式錯誤，往下改讀 .env 即可。
        pass

    # load_dotenv() 會讀取同資料夾或上層可找到的 .env 檔，
    # 讓 os.getenv() 可以拿到 OPENAI_API_KEY 等設定。
    load_dotenv()
    return os.getenv(name, default)


def create_client():
    """
    建立 OpenAI client，集中處理 API key 檢查。

    教學重點：
    - 不要在每個功能區塊重複建立 key 檢查邏輯。
    - 缺少 API key 時要 fail fast，讓錯誤訊息直接指出設定問題。
    - API key 只傳給 SDK，不顯示在 Streamlit 畫面或 log 中。

    Returns:
        已設定 API key 的 OpenAI client。

    Raises:
        RuntimeError: 找不到 OPENAI_API_KEY 時，提醒學生先設定 .env 或 Secrets。
    """
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("找不到 OPENAI_API_KEY，請設定 .env 或 Streamlit Secrets。")
    return OpenAI(api_key=api_key)


def ask_ai(user_input, system_prompt="你是有幫助的 AI 助理。"):
    """
    呼叫 OpenAI Responses API，取得一次性完整回覆。

    適合場景：
    - 摘要、分類、改寫等固定任務。
    - 回覆通常不需要逐字出現在畫面上。
    - 想讓程式流程保持簡單：送出 prompt，等待完整答案，再顯示結果。

    Args:
        user_input: 使用者輸入或程式組好的任務 prompt。
        system_prompt: 放在 instructions 的角色與任務規則。

    Returns:
        模型產生的文字回覆。
    """
    client = create_client()
    model = get_secret("OPENAI_MODEL", "gpt-5.4-mini")

    # Responses API 的三個核心欄位：
    # model 決定使用哪個模型；instructions 放系統規則；input 放本次任務內容。
    response = client.responses.create(
        model=model,
        instructions=system_prompt,
        input=user_input,
    )

    # 這個教學範例只處理文字輸出，因此直接讀 output_text。
    # 若之後加入 structured output，這裡會改成解析 JSON 或 Pydantic model。
    return response.output_text


def stream_ai(user_input, system_prompt="你是有幫助的 AI 助理。"):
    """
    呼叫 OpenAI Responses API 的串流模式，逐段產生文字。

    適合場景：
    - 聊天 UI，讓使用者看到答案逐步出現。
    - 回覆較長時，降低「按下送出後畫面沒有反應」的感覺。

    Args:
        user_input: 使用者輸入的聊天訊息。
        system_prompt: 放在 instructions 的角色與任務規則。

    Yields:
        模型輸出的文字片段，交給 st.write_stream() 即時顯示。
    """
    client = create_client()
    model = get_secret("OPENAI_MODEL", "gpt-5.4-mini")

    # stream=True 代表 SDK 會回傳事件串流，而不是一次回傳完整 response。
    stream = client.responses.create(
        model=model,
        instructions=system_prompt,
        input=user_input,
        stream=True,
    )
    for event in stream:
        # Responses API streaming 會送出多種事件，例如開始、文字增量、完成與錯誤。
        # 這個範例只把「文字 delta」交給畫面，其他事件先略過，降低初學負擔。
        if getattr(event, "type", None) == "response.output_text.delta":
            yield event.delta


def init_messages():
    """
    初始化聊天紀錄，避免每次互動後歷史訊息消失。

    Streamlit 的重要心智模型：
    - 使用者點按鈕、送出表單、輸入聊天訊息時，整支 app.py 會重新執行。
    - 一般 Python 變數會重設；st.session_state 會保留同一個瀏覽器 session 的資料。
    - 因此聊天紀錄要放在 st.session_state，而不是一般 list 變數。
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []


def add_message(role, content):
    """
    把一則訊息加入聊天紀錄。

    Args:
        role: 訊息角色，Streamlit chat UI 常用 "user" 或 "assistant"。
        content: 要顯示在聊天視窗中的文字。
    """
    st.session_state.messages.append({"role": role, "content": content})


def reset_messages():
    """
    清空聊天紀錄。

    這個函式只負責改狀態；呼叫端會再執行 st.rerun()，
    讓畫面立刻用清空後的 session_state 重新繪製。
    """
    st.session_state.messages = []


st.title("Week 7 Streamlit AI App")
st.caption("OpenAI Responses API + Streamlit streaming + session state")

# Sidebar 放全域設定，不佔用主要互動畫面。
# 這些設定會在每次 rerun 時重新讀取，但 widget 目前的值由 Streamlit 管理。
with st.sidebar:
    st.header("設定")
    system_prompt = st.text_area("System prompt", value="你是有幫助的 AI 助理。")
    use_streaming = st.toggle("使用串流回覆", value=True)
    if st.button("清空聊天紀錄"):
        reset_messages()
        st.rerun()

# 不顯示 key 內容，只提醒是否已設定。
# 教學時可強調：檢查 secret 存不存在可以，絕對不要 st.write(api_key)。
if not get_secret("OPENAI_API_KEY"):
    st.warning("尚未設定 OPENAI_API_KEY。請建立 .env 或在 Streamlit Secrets 中設定。")

# 用 tabs 把聊天、摘要、檔案工具分開，避免單頁內容過長。
tab_chat, tab_summary, tab_file = st.tabs(["聊天", "摘要", "檔案"])

with tab_chat:
    # 聊天功能一定要先初始化 session_state，下面的歷史訊息迴圈才有資料可讀。
    init_messages()

    # 每次 rerun 都先重畫歷史訊息。
    # 如果少了這段，送出新訊息後舊訊息仍在 session_state，但畫面不會顯示出來。
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # st.chat_input 在沒有新輸入時會回傳 None；使用者送出後才進入 if prompt 區塊。
    prompt = st.chat_input("請輸入問題")
    if prompt:
        # 先把 user 訊息寫入紀錄，再立即畫到畫面上，讓使用者確認送出的內容。
        add_message("user", prompt)
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            if use_streaming:
                # st.write_stream() 會一邊接收 generator 的文字片段，一邊更新畫面；
                # 執行完成後，它會回傳完整字串，方便放回聊天紀錄。
                answer = st.write_stream(stream_ai(prompt, system_prompt))
            else:
                # 非串流模式適合用來對照：畫面會等 API 回傳完整答案後才一次顯示。
                answer = ask_ai(prompt, system_prompt)
                st.write(answer)

        # assistant 回覆完成後才存入紀錄，避免串流中斷時留下不完整內容。
        add_message("assistant", answer)

with tab_summary:
    # 表單適合固定任務：使用者填完欄位後再一次送出。
    # 這可以避免學生每打一個字或每換一個選項就觸發昂貴的 API 呼叫。
    with st.form("summary_form"):
        source_text = st.text_area("貼上要摘要的文字", height=180)
        style = st.selectbox("摘要風格", ["條列重點", "一段式摘要", "給主管看的摘要"])
        submitted = st.form_submit_button("產生摘要")
    if submitted and source_text:
        # 把 UI 選項轉成明確 prompt，示範「介面輸入」如何變成「模型任務」。
        prompt = f"請將以下內容整理成{style}：\n\n{source_text}"
        st.subheader("摘要結果")
        st.write(ask_ai(prompt, system_prompt="你是嚴謹的摘要助理。"))

with tab_file:
    # 第 7 週先處理純文字檔；PDF / Word / CSV 會在後續文件處理週延伸。
    # 這裡刻意限制副檔名，讓學生先專注在「上傳 -> 讀文字 -> 丟給 AI」的主流程。
    uploaded_file = st.file_uploader("上傳 .txt 或 .md 檔案", type=["txt", "md"])
    if uploaded_file is not None:
        # uploaded_file.read() 取得的是 bytes；純文字 app 需要用 UTF-8 解碼成 str。
        text = uploaded_file.read().decode("utf-8")

        # 預覽只顯示前 2000 字，避免大檔案把畫面撐得太長。
        st.text_area("檔案內容預覽", text[:2000], height=200)
        if st.button("摘要這份檔案"):
            # 控制輸入長度，避免單次測試成本過高。
            # 真正產品會用 token 計算或分段摘要；這裡用字數截斷作為入門示範。
            prompt = "請摘要以下文字，列出 5 個重點：\n\n" + text[:12000]
            st.write(ask_ai(prompt, system_prompt="你是文件摘要助理。"))
