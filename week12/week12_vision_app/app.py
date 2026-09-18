"""第 12 週 Streamlit 圖片理解工具。

畫面先完成本機圖片驗證與預覽；只有使用者送出表單後才呼叫 OpenAI API，
避免 Streamlit rerun 因切換控制項或展開區塊而重複產生成本。
"""

from __future__ import annotations

import json

import streamlit as st

from vision_utils import (
    DEFAULT_MODEL,
    MAX_FILE_BYTES,
    analyze_image,
    get_secret,
    validate_image,
)


st.set_page_config(
    page_title="Week 12 圖片理解工具",
    page_icon=":material/image_search:",
    layout="wide",
)

st.session_state.setdefault("vision_result", None)
st.session_state.setdefault("vision_result_mode", None)

with st.sidebar:
    st.header("圖片理解設定")
    mode = st.segmented_control(
        "任務模式",
        ["圖片描述", "圖片問答", "截圖檢查", "收據／表單抽取"],
        default="圖片描述",
        required=True,
        width="stretch",
    )
    detail = st.segmented_control(
        "圖片細節",
        ["auto", "low", "high"],
        default="auto",
        required=True,
        width="stretch",
        help="low 適合粗略理解；high 適合小字或文件；auto 交由模型決定。",
    )
    model = get_secret("OPENAI_MODEL", DEFAULT_MODEL)
    st.caption(f"模型：`{model}`")
    st.warning("圖片會傳送到 OpenAI API，且圖片輸入會計入 token 與費用。")
    st.error("不得上傳個資、機密、醫療影像、未授權內容或 CAPTCHA。")

st.title("Week 12 圖片理解工具")
st.caption("圖片描述、圖片問答、截圖理解與收據／表單結構化抽取")

if not get_secret("OPENAI_API_KEY"):
    st.warning(
        "尚未設定 OPENAI_API_KEY。你仍可測試圖片驗證與預覽；送出分析時會顯示設定提示。"
    )

uploaded = st.file_uploader(
    "上傳 PNG、JPEG、WEBP 或非動態 GIF",
    type=["png", "jpg", "jpeg", "webp", "gif"],
    max_upload_size=MAX_FILE_BYTES // (1024 * 1024),
    help="單檔上限 8 MB；上傳器的副檔名篩選不是安全驗證，程式仍會檢查檔案內容。",
)

if uploaded is None:
    with st.container(border=True):
        st.subheader("課堂測試建議")
        st.markdown(
            "- 一張無個資的生活照片：比較圖片描述與自由問答。\n"
            "- 自己製作的錯誤畫面截圖：測試可見文字與排錯建議。\n"
            "- `sample_data/create_demo_receipt.py` 產生的虛構收據：測試結構化抽取。"
        )
    st.stop()

file_bytes = uploaded.getvalue()
try:
    metadata = validate_image(file_bytes)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

preview_col, info_col = st.columns([3, 2], vertical_alignment="top")
with preview_col:
    with st.container(border=True):
        st.subheader("圖片預覽")
        st.image(file_bytes, caption=uploaded.name, width="stretch")
with info_col:
    with st.container(border=True):
        st.subheader("本機檢查")
        st.metric("尺寸", f"{metadata['width']} × {metadata['height']}")
        st.metric("檔案大小", f"{metadata['megabytes']:.3f} MB")
        st.write(f"偵測格式：`{metadata['mime_type']}`")
        st.success("圖片通過本機格式與大小檢查，尚未呼叫 API。")

with st.form("vision_analysis_form", border=True):
    if mode == "圖片問答":
        question = st.text_input(
            "想詢問圖片的問題",
            placeholder="例如：畫面中的錯誤訊息指出哪個設定缺失？",
        )
    else:
        question = ""
        st.caption("此模式使用教材預先設計的任務 prompt。")

    submitted = st.form_submit_button(
        "分析圖片",
        type="primary",
        icon=":material/image_search:",
    )

if submitted:
    try:
        with st.spinner("正在分析圖片；請勿重複送出..."):
            result = analyze_image(
                file_bytes,
                mode=mode,
                question=question,
                detail=detail,
                model=model,
            )
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"圖片分析失敗：{exc}")
    else:
        # 只有完整成功後才更新結果，避免舊結果被半成品覆蓋。
        st.session_state["vision_result"] = result
        st.session_state["vision_result_mode"] = mode

result = st.session_state.get("vision_result")
if result is not None:
    st.divider()
    st.subheader(f"分析結果｜{st.session_state['vision_result_mode']}")
    if isinstance(result, dict):
        metric_left, metric_right = st.columns(2)
        metric_left.metric("文件類型", result["document_type"])
        total_text = "無法確認" if result["total"] is None else str(result["total"])
        metric_right.metric("總額", total_text)
        st.write(f"商家／機構：{result['merchant'] or '無法確認'}")
        st.write(f"日期：{result['date'] or '無法確認'}")
        st.write(f"幣別：{result['currency'] or '無法確認'}")

        st.markdown("#### 品項")
        if result["items"]:
            st.dataframe(result["items"], width="stretch", hide_index=True)
        else:
            st.info("沒有可確認的品項。")

        st.markdown("#### 注意事項")
        if result["warnings"]:
            for warning in result["warnings"]:
                st.markdown(f"- {warning}")
        else:
            st.write("模型未列出額外警告；仍應人工核對原圖。")

        with st.expander("查看 structured output JSON"):
            st.code(json.dumps(result, ensure_ascii=False, indent=2), language="json")
    else:
        st.markdown(result)

    st.info("Vision 回答可能出錯；文字、數字、計數與重要決策都必須回看原圖人工核對。")

