import streamlit as st

# TODO A：修改標題與說明，先看見一個可以操作的畫面。
st.title("TODO：填入你的App標題")
st.write("輸入稱呼，按送出才顯示問候；本例不呼叫API。")
name = st.text_input("你的稱呼", max_chars=30)
if st.button("送出"):
    if name.strip():
        st.write("你好，", name)
    else:
        st.warning("請先輸入稱呼。")
