import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
def stream_answer(messages):
    """完整提供的串流段：逐片yield，確認完成後才結束。"""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("缺少金鑰")
    client = OpenAI(api_key=key, max_retries=0, timeout=60.0)
    completed = False
    # with確保失敗或中止離開時關閉串流連線。
    with client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"), store=False,
        instructions="你是課程助理，回答簡潔；不確定就說明，不憑空補充。",
        input=messages, stream=True) as events:
        for event in events:
            if event.type == "response.output_text.delta":
                yield event.delta
            elif event.type == "response.completed":
                completed = event.response.status == "completed"
                for output in event.response.output:
                    if output.type == "message":
                        for content in output.content:
                            if content.type == "refusal":
                                raise ValueError("模型拒答")
            elif event.type in ["error", "response.failed", "response.incomplete", "response.refusal.delta", "response.refusal.done"]:
                raise ValueError("串流失敗、未完成或拒答")
    if not completed:
        raise ValueError("沒有收到完成事件")

st.title("課程聊天助理：串流版")
enable_api = st.checkbox("啟用真實API（每則問題1次請求）", value=False)
st.caption("預設離線固定回覆，只測畫面與保存；不代表模型理解或記住前文。切換模式會清空紀錄。")
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat_mode = enable_api
if st.session_state.chat_mode != enable_api:
    st.session_state.messages = []
    st.session_state.chat_mode = enable_api
if st.button("清空聊天紀錄"):
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
prompt = st.chat_input("請輸入問題（最多1000字元）", max_chars=1000)
if prompt and prompt.strip():
    with st.chat_message("user"):
        st.write(prompt)
    # 畫面紀錄不是模型記憶；必須將最近五輪與本輪問題放進API的input。
    messages = st.session_state.messages[-10:] + [{"role": "user", "content": prompt}]
    try:

        with st.chat_message("assistant"):
            if enable_api:
                answer = st.write_stream(stream_answer(messages))
            else:
                # 固定片段只示範串接，不是模型成果，也不測量回應速度。
                answer = st.write_stream(["離線片段示範：", "已收到「", prompt, "」，沒有呼叫模型。"])
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("沒有完整的非空回答")

    except Exception as exc:
        st.error("這輪未加入紀錄；請檢查設定或回應。錯誤類型：" + type(exc).__name__)
    else:
        # 只有完整成功才保存user與assistant配對；失敗不留半輪。
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": answer})
