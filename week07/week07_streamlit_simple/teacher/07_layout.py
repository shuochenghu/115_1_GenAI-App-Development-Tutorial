import streamlit as st

st.title("側欄與分頁：先看版面用途")
with st.sidebar:
    display = st.selectbox("顯示方式", ["詳細", "精簡"])
card, notes = st.tabs(["活動卡", "操作說明"])
with card:
    st.subheader("AI專題討論")
    if display == "詳細":
        st.write("下週三14:00，A203；負責人尚未指定。")
with notes:
    st.write("側欄放設定；分頁整理內容。本例0次API。")
    st.caption("分頁不是API開關；付費工作仍要放在明確送出動作之後。")
