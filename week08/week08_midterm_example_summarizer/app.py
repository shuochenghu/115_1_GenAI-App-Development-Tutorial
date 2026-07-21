import json
import os

from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st


st.set_page_config(page_title="Week 8 AI Summarizer Demo", layout="centered")


MAX_INPUT_CHARS = 12000
APP_TITLE = "AI 摘要與行動項目整理器"
APP_DESCRIPTION = "將長文整理成摘要、重點、關鍵字與待辦事項，示範期中小專題的完整結構。"
SYSTEM_PROMPT = """
你是嚴謹的文件摘要助理。
你的任務是根據使用者提供的原文整理摘要、重點、關鍵字與待辦事項。

請遵守：
1. 只能根據原文內容整理，不要捏造原文沒有出現的事實。
2. 如果原文資訊不足，請在 summary 或 action_items 中明確指出。
3. 文字要清楚、精簡，適合課堂 demo 使用。
4. 所有輸出必須符合指定 JSON Schema。
"""


SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "適合顯示在結果區的短標題。",
        },
        "summary": {
            "type": "string",
            "description": "用 2 到 4 句話整理原文核心內容。",
        },
        "key_points": {
            "type": "array",
            "description": "原文中最重要的 3 到 6 個重點。",
            "items": {"type": "string"},
        },
        "keywords": {
            "type": "array",
            "description": "3 到 8 個關鍵字。",
            "items": {"type": "string"},
        },
        "action_items": {
            "type": "array",
            "description": "可執行的後續行動。若原文沒有待辦，也要說明沒有明確待辦。",
            "items": {"type": "string"},
        },
    },
    "required": ["title", "summary", "key_points", "keywords", "action_items"],
    "additionalProperties": False,
}


SAMPLE_TEXT = """
本週專案會議確認期中小專題以 Streamlit Web App 作為主要成果。
每位同學需要完成一個可以本機執行的 AI 應用，並將程式上傳到 GitHub。
App 必須至少呼叫一次 OpenAI API，並設計一項 structured output，
例如摘要器可以輸出標題、摘要、重點、關鍵字與待辦事項。

老師提醒同學不要把 API key 寫在程式碼或 README 裡，也不要把 .env 上傳到 GitHub。
下週課堂會安排 3 到 5 分鐘 demo，展示 App 解決的問題、操作流程與 AI 回傳結果。
如果時間足夠，學生可以嘗試部署到 Streamlit Community Cloud 作為加分。
"""


def get_secret(name, default=None):
    """
    讀取 OpenAI 設定，支援 Streamlit Secrets 與本機 `.env`。

    教師 demo 會在本機與雲端兩種環境使用，因此不能只依賴單一來源。
    這個 helper 讓 API key 與模型名稱統一從 `get_secret()` 取得，
    也避免在主流程中重複撰寫環境判斷。

    參數 (Args):
        name: 設定名稱，例如 `OPENAI_API_KEY` 或 `OPENAI_MODEL`。
        default: 找不到設定時使用的預設值。

    回傳 (Returns):
        設定值字串；若找不到則回傳 default。
    """

    # 情況一：部署環境使用 Streamlit Secrets。
    # 注意：不要把 secrets 的內容顯示在畫面上。
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        # 情況二：本機尚未建立 secrets 檔，改讀 `.env`。
        pass

    load_dotenv()
    return os.getenv(name, default)


def create_client():
    """
    建立 OpenAI client，並處理 API key 缺漏情境。

    專題 App 應該在缺少 API key 時給出可操作的提示，
    而不是讓 SDK 產生學生難以理解的錯誤訊息。

    回傳 (Returns):
        OpenAI client。

    可能錯誤 (Raises):
        RuntimeError: 未設定 `OPENAI_API_KEY`。
    """

    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("找不到 OPENAI_API_KEY，請先設定 `.env` 或 Streamlit Secrets。")
    return OpenAI(api_key=api_key)


def build_summary_prompt(source_text, audience, style):
    """
    將使用者輸入整理成摘要任務 prompt。

    這裡把「原文」「讀者」「摘要風格」分開寫，是為了降低 prompt 混淆。
    對學生來說，這也示範了專題中應該把任務規格集中管理，
    不要把關鍵指令分散在多個 UI callback 裡。

    參數 (Args):
        source_text: 使用者貼上的原始文字。
        audience: 摘要預期讀者，例如同學、老師、主管。
        style: 摘要語氣或格式。

    回傳 (Returns):
        完整 prompt 字串。
    """

    return f"""
請根據以下原文產生摘要結果。

預期讀者：
{audience}

摘要風格：
{style}

原文：
{source_text}

請保留原文中的重要限制、期限、風險與待辦事項。
如果原文沒有明確待辦事項，請在 action_items 欄位說明沒有明確待辦。
"""


def summarize_text(source_text, audience, style):
    """
    呼叫 OpenAI Responses API，取得符合 `SUMMARY_SCHEMA` 的摘要結果。

    此函式是 demo App 的核心業務邏輯。Streamlit UI 只負責收集輸入與顯示結果；
    API 呼叫、schema 契約與 JSON 解析集中在這裡，方便之後測試與重用。

    參數 (Args):
        source_text: 要摘要的文字。
        audience: 使用者指定的讀者。
        style: 使用者指定的摘要風格。

    回傳 (Returns):
        dict，包含 title、summary、key_points、keywords、action_items。

    可能錯誤 (Raises):
        RuntimeError: API 無回應或 JSON 解析失敗。
    """

    client = create_client()
    model = get_secret("OPENAI_MODEL", "gpt-5.4-mini")
    prompt = build_summary_prompt(source_text, audience, style)

    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "summary_result",
                "schema": SUMMARY_SCHEMA,
                "strict": True,
            }
        },
    )

    if not response.output_text:
        raise RuntimeError("AI 沒有回傳摘要結果，請稍後再試或縮短輸入文字。")

    try:
        return json.loads(response.output_text)
    except json.JSONDecodeError as exc:
        # Structured Outputs 正常情況下會遵守 schema。
        # 這個保護仍然保留，因為正式 App 不應假設外部服務永遠回傳可解析內容。
        raise RuntimeError("AI 回傳格式無法解析，請檢查 schema 或模型設定。") from exc


def stream_ai(user_input, system_prompt=SYSTEM_PROMPT):
    """
    可選加分示範：用 streaming 逐段顯示一段式摘要。

    教師 demo 的主要結果仍使用 structured output，因為期中專題最低要求是
    讓程式能穩定讀取欄位。streaming 放在結果下方作為額外示範，
    用來說明學生若想做聊天感或即時回饋，可以如何延伸。

    參數 (Args):
        user_input: 要送給模型的 prompt。
        system_prompt: 控制 AI 角色、任務規則與限制的系統指令。

    產生 (Yields):
        模型逐段輸出的文字片段。
    """

    client = create_client()
    model = get_secret("OPENAI_MODEL", "gpt-5.4-mini")
    stream = client.responses.create(
        model=model,
        instructions=system_prompt,
        input=user_input,
        stream=True,
    )

    for event in stream:
        if getattr(event, "type", None) == "response.output_text.delta":
            yield event.delta


def render_summary(summary_data):
    """
    將 structured output 轉成適合使用者閱讀的畫面。

    這個函式刻意不只顯示原始 JSON，而是把不同欄位拆成摘要、重點、
    關鍵字與待辦事項。這是期中專題需要展示的 App 化能力。

    參數 (Args):
        summary_data: `summarize_text()` 回傳的 dict。
    """

    st.subheader(summary_data["title"])
    st.write(summary_data["summary"])

    col_left, col_right = st.columns(2)
    with col_left:
        st.metric("重點數", len(summary_data["key_points"]))
    with col_right:
        st.metric("關鍵字數", len(summary_data["keywords"]))

    st.markdown("#### 重點整理")
    for item in summary_data["key_points"]:
        st.markdown(f"- {item}")

    st.markdown("#### 關鍵字")
    st.write("、".join(summary_data["keywords"]))

    st.markdown("#### 待辦事項")
    for item in summary_data["action_items"]:
        st.markdown(f"- {item}")

    with st.expander("查看 structured output JSON"):
        st.json(summary_data)


def read_source_text():
    """
    從「貼上文字」或「上傳檔案」取得要摘要的內容。

    第 8 週 demo 加入檔案上傳，是為了讓學生看到 Streamlit App 可以從第 7 週
    的 `st.file_uploader()` 延伸到專題輸入流程。這裡仍只處理 `.txt` / `.md`，
    PDF、Word、CSV 等格式會留到後續文件處理週，不在期中專題 starter 中增加負擔。

    回傳 (Returns):
        使用者提供的文字；若同時有檔案與貼上文字，優先使用檔案內容。
    """

    tab_text, tab_file = st.tabs(["貼上文字", "上傳檔案"])

    with tab_text:
        pasted_text = st.text_area(
            "貼上要摘要的文字",
            height=260,
            placeholder="貼上會議記錄、課堂筆記、公告或文章片段。",
        )

    with tab_file:
        uploaded_file = st.file_uploader("上傳 .txt 或 .md 檔案", type=["txt", "md"])
        file_text = ""
        if uploaded_file is not None:
            # 教學範例先假設文字檔以 UTF-8 為主；errors='ignore' 避免少數編碼問題讓 demo 中斷。
            file_text = uploaded_file.read().decode("utf-8", errors="ignore")
            st.text_area("檔案內容預覽", file_text[:2000], height=180, disabled=True)

    return (file_text or pasted_text).strip()


def main():
    """
    Streamlit demo 主流程。

    流程設計：
    1. 顯示 App 目的與安全提醒。
    2. 收集原文、讀者與摘要風格。
    3. 在 API 呼叫前檢查空白與長度。
    4. 呼叫 structured output helper。
    5. 用多個 UI 區塊呈現結果。
    """

    st.title(APP_TITLE)
    st.caption(APP_DESCRIPTION)

    with st.sidebar:
        st.header("Demo 說明")
        st.markdown("此範例示範期中專題應具備的基本結構。")
        st.markdown("- Streamlit 表單")
        st.markdown("- OpenAI API helper")
        st.markdown("- Structured Outputs")
        st.markdown("- 文字貼上與 .txt/.md 檔案上傳")
        st.markdown("- 選做 streaming 示範")
        st.markdown("- API key 安全管理")
        st.markdown("- 錯誤處理與輸入限制")
        st.divider()
        st.caption("本範例不是學生可直接照抄繳交的題目。")
        st.error("紅線：API key 只能放 `.env` 或 Secrets，絕不可寫死或推上 GitHub。")

    if not get_secret("OPENAI_API_KEY"):
        st.warning("尚未設定 OPENAI_API_KEY。請建立 `.env` 或在 Streamlit Secrets 中設定。")

    with st.expander("範例輸入文字"):
        st.text_area("可複製的 demo 文字", SAMPLE_TEXT.strip(), height=220, disabled=True)

    source_text = read_source_text()
    audience = st.selectbox("摘要讀者", ["修課同學", "授課教師", "專案主管", "一般讀者"])
    style = st.selectbox("摘要風格", ["條列清楚", "簡短正式", "適合簡報", "適合行動清單"])
    use_streaming = st.toggle("同時顯示一段式 streaming 摘要（加分示範）", value=False)
    submitted = st.button("產生摘要", type="primary")

    if not submitted:
        return

    # API 呼叫前先做本機檢查。這能降低成本，也能讓錯誤訊息更接近使用者行為。
    if not source_text.strip():
        st.error("請先貼上文字或上傳 .txt / .md 檔案。")
        return
    if len(source_text) > MAX_INPUT_CHARS:
        st.error(f"輸入文字過長，請先縮短到 {MAX_INPUT_CHARS} 字以內。")
        return

    try:
        with st.spinner("正在產生 structured summary..."):
            summary_data = summarize_text(source_text, audience, style)
        render_summary(summary_data)

        if use_streaming:
            st.divider()
            st.markdown("#### 一段式 streaming 摘要")
            st.write_stream(
                stream_ai(f"請用約 100 字中文摘要以下內容，避免加入原文沒有的資訊：\n\n{source_text}")
            )
    except RuntimeError as exc:
        st.error(str(exc))
    except Exception as exc:
        # 課堂 demo 顯示簡短錯誤即可；正式產品可另外接 logging 或監控。
        st.error(f"執行時發生未預期錯誤：{exc}")


if __name__ == "__main__":
    main()
