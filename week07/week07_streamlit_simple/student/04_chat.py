import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
st.title("課程聊天助理")
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

        if enable_api:
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                raise ValueError("缺少金鑰")
            client = OpenAI(api_key=key, max_retries=0, timeout=60.0)
            response = client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"), store=False,
                instructions="你是課程助理，回答簡潔；不確定就說明，不憑空補充。", input=messages)
            # 必要回應檢查已提供；拒答、未完成、空文字不當成成功。
            for output in response.output:
                if output.type == "message":
                    for content in output.content:
                        if content.type == "refusal":
                            raise ValueError("模型拒答")
            if response.status != "completed" or not response.output_text.strip():
                raise ValueError("沒有完成的非空回答")

            answer = response.output_text
        else:
            answer = "離線畫面示範：已收到「" + prompt + "」，沒有呼叫模型。"
        with st.chat_message("assistant"):
            st.write(answer)

    except Exception as exc:
        st.error("這輪未加入紀錄；請檢查設定或回應。錯誤類型：" + type(exc).__name__)
    else:
        # 只有完整成功才保存user與assistant配對；失敗不留半輪。
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": answer})
