# ============================================================
# 02 rerun與狀態保存
# ------------------------------------------------------------
# 教學重點：
#   1. 連按兩次加一，對照普通變數與session_state。
#   2. 狀態只在同一工作階段保留，不是資料庫或模型記憶。
#   3. B只完成歸零動作；先預測，再操作驗收。
#
# 啟動：python -m streamlit run teacher/02_state.py
# 請先進入week07/week07_streamlit_simple配套資料夾，並使用課程環境。
# 本例不呼叫API，所有操作都是0次請求。
# ============================================================

import streamlit as st

st.title("按鈕與狀態保存")


# ---------- 1. 比較普通變數與跨rerun狀態 ----------
# 普通變數每次都重設；session_state在同一工作階段的rerun間保留。
ordinary_count = 0

# 只在第一次沒有count時初始化；每次都指定0，就無法累加。
if "count" not in st.session_state:
    st.session_state.count = 0


# ---------- 2. 按一次，分別修改兩種計數 ----------
# 點加一會重新執行整份程式；普通變數從0開始，保存值接續上次。
if st.button("加一"):
    ordinary_count += 1
    st.session_state.count += 1


# ---------- 3. 歸零小練習 ----------
# B只處理保存的次數；不新增函式或第二份狀態。
if st.button("歸零"):
    st.session_state.count = 0  # 教師提醒（學生TODO B）：此處為歸零參考答案。


# ---------- 4. 顯示對照結果 ----------
# 連按兩次加一：普通值仍1、保存值為2。歸零後保存值為0。
st.write("普通變數：", ordinary_count)
st.write("保存的次數：", st.session_state.count)
st.caption("關閉／重新整理瀏覽器可能開始新工作階段；這不是資料庫。")
