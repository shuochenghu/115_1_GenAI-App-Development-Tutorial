"""第 12 週｜圖片理解工具 Streamlit App（Claude 版）。

流程：上傳圖片 → 本機驗證與預覽（不花錢）→ 選任務模式與 detail
     →（按「分析圖片」才）呼叫 Responses API → 顯示文字或結構化結果。

設計重點：
- **API 只在送出表單後呼叫**；切換側邊欄控制項或展開區塊不會重送。
- 結果存在 `st.session_state`，rerun 後仍會顯示。
- **離線示範模式**不需 API key：跑完驗證、prompt、request 預覽，回傳標註過的樣本結果，
  讓沒有金鑰的學生也能走完整個 UI 流程。
- 抽取模式先經 `normalize_receipt()` 再顯示，缺欄位顯示「無法確認」，不補假資料。

helper 命名（`validate_image` / `build_task_prompt` / `analyze_image` 等）對齊
Codex 版 `week12_vision_app/`，兩版可互換對照。
"""

from __future__ import annotations

import json

import streamlit as st

from vision_utils import (
    DEFAULT_MODEL,
    DETAIL_LEVELS,
    MAX_FILE_BYTES,
    TASK_MODES,
    analyze_image,
    build_request,
    choose_detail,
    get_secret,
    normalize_receipt,
    preview_request,
    validate_image,
)


st.set_page_config(page_title="Week 12 圖片理解工具", page_icon="🖼️", layout="wide")


def initialize_state() -> None:
    """集中建立本頁使用的 session state，避免 rerun 讀到不存在的 key。"""
    st.session_state.setdefault("vision_result", None)
    st.session_state.setdefault("vision_result_mode", None)
    st.session_state.setdefault("vision_result_offline", False)


def render_sidebar() -> tuple[str, str, bool, str]:
    """側邊欄設定；回傳 (mode, detail, offline, model)。"""
    with st.sidebar:
        st.header("⚙️ 設定")
        mode = st.radio("任務模式", TASK_MODES, index=0)
        suggested = choose_detail(mode)
        detail = st.selectbox(
            "圖片細節（detail）",
            DETAIL_LEVELS,
            index=DETAIL_LEVELS.index(suggested),
            help="low 適合粗略理解；high 適合小字或文件；auto 交由模型決定。",
        )
        st.caption(f"依任務模式建議：`{suggested}`（`choose_detail` 規則，可自行改）")
        st.divider()
        offline = st.checkbox(
            "離線示範模式（不呼叫 API）",
            value=False,
            help="跑完驗證、prompt 與 request 預覽，回傳標註過的樣本結果；不需 API key。",
        )
        model = get_secret("OPENAI_MODEL", DEFAULT_MODEL) or DEFAULT_MODEL
        if offline:
            st.warning("離線模式：結果是固定樣本，不是模型分析。")
        else:
            st.warning(f"線上模式：模型 `{model}`；圖片會傳到 OpenAI 並計入 token 費用。")
        st.divider()
        st.error("不得上傳個資、機密、醫療影像、未授權人像或 CAPTCHA。")
    return mode, detail, offline, model


def render_local_check(file_bytes: bytes, filename: str) -> dict | None:
    """本機驗證與預覽；失敗時顯示錯誤並回 None。這一步不呼叫 API。"""
    try:
        metadata = validate_image(file_bytes)
    except ValueError as exc:
        st.error(str(exc))
        return None

    preview_col, info_col = st.columns([3, 2])
    with preview_col:
        st.image(file_bytes, caption=filename)
    with info_col:
        st.subheader("本機檢查")
        st.metric("尺寸", f"{metadata['width']} × {metadata['height']}")
        st.metric("檔案大小", f"{metadata['megabytes']:.3f} MB")
        st.write(f"偵測格式：`{metadata['mime_type']}`（依檔案內容，不看副檔名）")
        st.success("通過本機格式與大小檢查；尚未呼叫 API。")
    return metadata


def render_receipt(result: dict) -> None:
    """顯示結構化抽取結果；缺值顯示「無法確認」，不補假資料。"""
    data = normalize_receipt(result)
    left, right = st.columns(2)
    left.metric("文件類型", data["document_type"])
    right.metric("總額", "無法確認" if data["total"] is None else str(data["total"]))
    st.write(f"商家／機構：{data['merchant'] or '無法確認'}")
    st.write(f"日期：{data['date'] or '無法確認'}")
    st.write(f"幣別：{data['currency'] or '無法確認'}")

    st.markdown("#### 品項")
    if data["items"]:
        st.dataframe(data["items"], hide_index=True)
    else:
        st.info("沒有可確認的品項。")

    st.markdown("#### 注意事項（warnings）")
    if data["warnings"]:
        for warning in data["warnings"]:
            st.markdown(f"- {warning}")
    else:
        st.write("模型未列出額外警告；仍應人工核對原圖。")

    with st.expander("structured output JSON"):
        st.code(json.dumps(data, ensure_ascii=False, indent=2), language="json")


def render_result() -> None:
    """顯示 session_state 中的最後一次結果（rerun 後仍在）。"""
    result = st.session_state.get("vision_result")
    if result is None:
        return
    st.divider()
    st.subheader(f"分析結果｜{st.session_state['vision_result_mode']}")
    if st.session_state.get("vision_result_offline"):
        st.info("這是離線示範樣本，不是模型分析結果。")
    if isinstance(result, dict):
        render_receipt(result)
    else:
        st.markdown(result)
    st.warning("Vision 可能看錯文字、數字、計數與位置；重要決策一定回看原圖人工核對。")


def main() -> None:
    initialize_state()
    st.title("🖼️ Week 12 圖片理解工具")
    st.caption("圖片描述、圖片問答、截圖檢查，以及收據／表單結構化抽取")

    mode, detail, offline, model = render_sidebar()

    if not offline and not get_secret("OPENAI_API_KEY"):
        st.warning("尚未設定 OPENAI_API_KEY。可先勾選「離線示範模式」走完流程；送出線上分析時會顯示設定提示。")

    uploaded = st.file_uploader(
        "上傳 PNG、JPEG、WEBP 或非動態 GIF（單檔上限 8 MB）",
        type=["png", "jpg", "jpeg", "webp", "gif"],
        help="上傳器的副檔名篩選不是安全驗證；程式仍會檢查檔案內容。",
    )
    if uploaded is None:
        st.markdown(
            "先上傳一張**不含敏感資料**的圖片：\n"
            "- 自己拍的生活照片：比較圖片描述與自由問答。\n"
            "- 自己製作的錯誤畫面截圖：測試截圖檢查。\n"
            "- `python sample_data/create_demo_receipt.py` 產生的虛構收據：測試結構化抽取。"
        )
        return

    if uploaded.size > MAX_FILE_BYTES:
        st.error(f"檔案超過 {MAX_FILE_BYTES // (1024 * 1024)} MB，請縮小後再試。")
        return

    file_bytes = uploaded.getvalue()
    if render_local_check(file_bytes, uploaded.name) is None:
        return

    with st.form("vision_form"):
        if mode == "圖片問答":
            question = st.text_input("想詢問圖片的問題", placeholder="例如：畫面中的錯誤訊息指出哪個設定缺失？")
        else:
            question = ""
            st.caption("此模式使用教材預先設計的任務 prompt（見 `build_task_prompt`）。")
        show_request = st.checkbox("送出前顯示 request 結構（data URL 截短）", value=offline)
        submitted = st.form_submit_button("分析圖片", type="primary")

    if not submitted:
        render_result()
        return

    if show_request:
        try:
            request = build_request(file_bytes, mode=mode, question=question, detail=detail, model=model)
        except ValueError as exc:
            st.error(str(exc))
            return
        with st.expander("將送出的 request（預覽）", expanded=True):
            st.code(json.dumps(preview_request(request), ensure_ascii=False, indent=2), language="json")

    try:
        with st.spinner("分析圖片中…請勿重複送出"):
            result = analyze_image(
                file_bytes, mode=mode, question=question, detail=detail, model=model, offline=offline
            )
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))
        return
    except Exception as exc:  # noqa: BLE001
        st.error(f"圖片分析失敗：{exc}")
        return

    # 只有完整成功後才更新結果，避免舊結果被半成品覆蓋。
    st.session_state["vision_result"] = result
    st.session_state["vision_result_mode"] = mode
    st.session_state["vision_result_offline"] = offline
    render_result()


if __name__ == "__main__":
    main()
