import streamlit as st

st.title("按鈕與狀態保存")
# 普通變數每次都重設；session_state在同一工作階段的rerun間保留。
ordinary_count = 0
if "count" not in st.session_state:
    st.session_state.count = 0
if st.button("加一"):
    ordinary_count += 1
    st.session_state.count += 1
if st.button("歸零"):
    st.info("TODO B：把session_state中的count改為0。")
st.write("普通變數：", ordinary_count)
st.write("保存的次數：", st.session_state.count)
st.caption("關閉／重新整理瀏覽器可能開始新工作階段；這不是資料庫。")
