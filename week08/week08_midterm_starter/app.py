import json
import os

from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st


# 頁面設定必須在其他 Streamlit 元件之前執行。
# 這裡的標題與說明會是使用者打開 App 後最先看到的訊號，
# 因此請讓它明確對應你的期中專題，而不是保留成一般聊天工具。
st.set_page_config(page_title="Week 8 Midterm Starter", layout="centered")


# TODO: 將下列三個常數改成你的專題設定。
# 建議先把「使用者是誰、要解決什麼問題、AI 不應該做什麼」寫清楚，
# 後面的 prompt、schema 與 UI 才會有一致的方向。
PROJECT_TITLE = "TODO：請填入你的期中小專題名稱"
PROJECT_DESCRIPTION = "TODO：請用一句話說明這個 App 解決什麼問題"
SYSTEM_PROMPT = """
TODO：請改寫成你的 App 專用 system prompt。

建議包含：
1. AI 扮演什麼角色。
2. 使用者會提供什麼資料。
3. AI 應該輸出什麼內容。
4. 不確定時要如何回答。
5. 哪些情況不能假裝知道答案。
"""


# TODO: 將這份 schema 改成你的 structured output 設計。
# Structured Outputs 的重點不是「讓 JSON 看起來漂亮」，
# 而是讓程式能穩定讀取欄位。欄位名稱、型態與 required 都應該對應你的 App 功能。
DEFAULT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "本次分析結果的短標題。",
        },
        "summary": {
            "type": "string",
            "description": "用 2 到 3 句話說明 AI 的主要判斷。",
        },
        "key_points": {
            "type": "array",
            "description": "列出最重要的 3 到 5 個重點。",
            "items": {"type": "string"},
        },
        "next_steps": {
            "type": "array",
            "description": "給使用者的後續行動建議。",
            "items": {"type": "string"},
        },
    },
    "required": ["title", "summary", "key_points", "next_steps"],
    "additionalProperties": False,
}


def get_secret(name, default=None):
    """
    讀取環境設定，支援本機 `.env` 與 Streamlit Cloud 的 `st.secrets`。

    本機開發時，學生通常會把 API key 放在 `.env`；
    部署到 Streamlit Cloud 時，則會改放在雲端後台的 Secrets。
    這個函式把兩種情況包成同一個入口，讓其他程式不用關心目前在哪個環境執行。

    參數 (Args):
        name: 要讀取的環境變數名稱，例如 `OPENAI_API_KEY`。
        default: 找不到設定時要回傳的預設值。

    回傳 (Returns):
        設定值字串；若兩種來源都找不到，回傳 default。
    """

    # 情況一：部署在 Streamlit Cloud。
    # st.secrets 不應該被印出或顯示在畫面上，只需要檢查是否存在。
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        # 情況二：本機執行時可能沒有 secrets 檔。
        # 這不是錯誤，後面會改讀 `.env`。
        pass

    # 本機開發用 `.env`。此檔應列入 `.gitignore`，避免把 API key 推到 GitHub。
    load_dotenv()
    return os.getenv(name, default)


def create_client():
    """
    建立 OpenAI client，並在缺少 API key 時給出清楚錯誤。

    這裡採用 fail-fast 設計：如果沒有 API key，就立刻停止 API 呼叫流程。
    這比讓錯誤一路傳到 OpenAI SDK 再出現模糊訊息更適合教學與除錯。

    回傳 (Returns):
        已設定 API key 的 OpenAI client。

    可能錯誤 (Raises):
        RuntimeError: 找不到 `OPENAI_API_KEY` 時拋出，讓 UI 可以顯示可理解的提示。
    """

    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("找不到 OPENAI_API_KEY，請設定 .env 或 Streamlit Secrets。")
    return OpenAI(api_key=api_key)


def build_prompt(source_text, task_goal, output_style):
    """
    將使用者表單輸入整理成要送給 LLM 的 prompt。

    prompt 建議集中在這個函式中組裝，不要散落在 Streamlit UI 裡。
    這樣做的好處是：未來要測試 prompt、改欄位、加入範例或做版本紀錄時，
    可以只改這個函式，不必翻整個 App。

    參數 (Args):
        source_text: 使用者貼上的主要資料。
        task_goal: 使用者希望 AI 完成的任務。
        output_style: 使用者選擇的輸出風格。

    回傳 (Returns):
        一段完整 prompt 字串。
    """

    # TODO: 依你的專題重新設計 prompt。
    # 建議保留「任務」「輸入資料」「限制」「輸出期待」四個區塊，
    # 因為這比單句指令更容易產生穩定結果。
    return f"""
請根據下列資料完成任務。

任務目標：
{task_goal}

輸出風格：
{output_style}

使用者提供的資料：
{source_text}

請避免捏造原文沒有提供的事實；如果資訊不足，請明確說明不足之處。
"""


def ask_ai(user_input, system_prompt=SYSTEM_PROMPT):
    """
    呼叫 OpenAI Responses API，取得一般文字回覆。

    此函式適合用在「摘要」「改寫」「建議」等文字型任務。
    如果你的 App 需要程式穩定讀取欄位，請改用 `extract_structured()`。

    參數 (Args):
        user_input: 要送給模型的 prompt。
        system_prompt: 控制 AI 角色、語氣、限制與安全邊界的系統指令。

    回傳 (Returns):
        模型回傳的文字。
    """

    client = create_client()
    model = get_secret("OPENAI_MODEL", "gpt-5.4-mini")
    response = client.responses.create(
        model=model,
        instructions=system_prompt,
        input=user_input,
    )

    # output_text 是 Responses API 中最常用的文字結果入口。
    # 如果你的模型回傳空字串，通常代表 prompt、模型可用性或安全拒答需要進一步檢查。
    if not response.output_text:
        raise RuntimeError("AI 沒有回傳文字內容，請檢查 prompt 或稍後再試。")
    return response.output_text


def stream_ai(user_input, system_prompt=SYSTEM_PROMPT):
    """
    可選加分功能：用 streaming 逐段顯示一般文字回覆。

    第 8 週最低要求仍以 structured output 為主；streaming 是加分項。
    因此 starter 不會在主流程預設啟用這個函式，避免學生同時改太多地方。
    如果你的專題需要即時感，例如聊天助理或逐段摘要，可以把這個 helper
    搭配 `st.write_stream()` 放到結果顯示區。

    參數 (Args):
        user_input: 要送給模型的 prompt。
        system_prompt: 控制 AI 角色、語氣、限制與安全邊界的系統指令。

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
        # Responses API streaming 會送出多種事件。
        # 這裡只取文字 delta；其他事件例如 completed 或 error 可在進階版再處理。
        if getattr(event, "type", None) == "response.output_text.delta":
            yield event.delta


def extract_structured(user_input, schema=DEFAULT_SCHEMA, system_prompt=SYSTEM_PROMPT):
    """
    呼叫 OpenAI Responses API，要求模型依 JSON Schema 回傳結構化結果。

    Structured Outputs 適合期中專題，因為它能讓 App 後續用固定欄位顯示結果，
    例如 `summary` 放摘要、`key_points` 放重點列表、`next_steps` 放建議。

    參數 (Args):
        user_input: 要分析的完整 prompt。
        schema: JSON Schema，定義模型必須回傳的欄位與型態。
        system_prompt: 控制 AI 角色、任務規則與限制的系統指令。

    回傳 (Returns):
        Python dict，欄位會依 schema 對齊。

    可能錯誤 (Raises):
        RuntimeError: API 沒有回傳內容或 JSON 解析失敗時拋出。
    """

    client = create_client()
    model = get_secret("OPENAI_MODEL", "gpt-5.4-mini")

    response = client.responses.create(
        model=model,
        instructions=system_prompt,
        input=user_input,
        text={
            "format": {
                "type": "json_schema",
                "name": "midterm_result",
                "schema": schema,
                "strict": True,
            }
        },
    )

    if not response.output_text:
        raise RuntimeError("AI 沒有回傳 structured output，請檢查 schema 或 prompt。")

    try:
        return json.loads(response.output_text)
    except json.JSONDecodeError as exc:
        # 即使使用 Structured Outputs，也保留解析錯誤處理。
        # 這能避免 UI 直接顯示一大串 traceback，學生也較容易定位問題。
        raise RuntimeError("AI 回傳內容無法解析成 JSON，請檢查 schema 設計。") from exc


def render_project_form():
    """
    顯示主要輸入表單，並回傳使用者填寫的內容。

    Streamlit 表單適合固定任務：使用者填完欄位後按一次送出，
    App 再呼叫 API。這比每改一個欄位就 rerun 並呼叫 API 更能控制成本。

    回傳 (Returns):
        tuple: source_text, task_goal, output_style, use_structured, submitted。
    """

    with st.form("midterm_form"):
        # TODO: 依你的專題修改欄位名稱與提示文字。
        source_text = st.text_area(
            "輸入資料",
            height=220,
            placeholder="貼上要分析、摘要、分類或改寫的文字。",
        )
        task_goal = st.text_input(
            "任務目標",
            value="TODO：請描述你希望 AI 完成的任務",
        )
        output_style = st.selectbox(
            "輸出風格",
            ["條列重點", "給初學者看的說明", "給主管看的摘要", "正式報告語氣"],
        )
        use_structured = st.toggle("使用 Structured Outputs", value=True)
        submitted = st.form_submit_button("產生結果")

    return source_text, task_goal, output_style, use_structured, submitted


def render_structured_result(result):
    """
    將 structured output 顯示成使用者容易閱讀的畫面。

    App 不應只把 JSON 原樣丟給使用者。開發者應該把欄位轉成標題、條列、
    表格或指標，讓使用者能快速理解 AI 結果。

    參數 (Args):
        result: `extract_structured()` 回傳的 dict。
    """

    st.subheader(result.get("title", "分析結果"))
    st.write(result.get("summary", ""))

    st.markdown("#### 重點")
    for item in result.get("key_points", []):
        st.markdown(f"- {item}")

    st.markdown("#### 後續建議")
    for item in result.get("next_steps", []):
        st.markdown(f"- {item}")

    with st.expander("查看原始 JSON"):
        st.json(result)


def main():
    """
    Streamlit App 主要流程。

    這裡負責畫面排序與事件流程：
    1. 顯示專題說明。
    2. 檢查 API key 狀態。
    3. 收集使用者輸入。
    4. 驗證輸入是否合理。
    5. 呼叫 OpenAI API。
    6. 顯示結果或錯誤訊息。
    """

    st.title(PROJECT_TITLE)
    st.caption(PROJECT_DESCRIPTION)

    with st.sidebar:
        st.header("專題檢核")
        st.markdown("- 已設定 App 名稱")
        st.markdown("- 已設計 system prompt")
        st.markdown("- 已設計 structured output")
        st.markdown("- 已完成 README")
        st.markdown("- 已確認 API key 不會上傳 GitHub")
        st.divider()
        st.caption("提示：這個 sidebar 可改成你的專題設定或使用說明。")

    if not get_secret("OPENAI_API_KEY"):
        st.warning("尚未設定 OPENAI_API_KEY。請建立 `.env` 或在 Streamlit Secrets 中設定。")

    st.info("請先完成 app.py 裡的 TODO，再把這個 starter 改造成你的期中小專題。")

    source_text, task_goal, output_style, use_structured, submitted = render_project_form()

    if not submitted:
        return

    # 輸入驗證放在 API 呼叫前，避免把空白或過長內容送到模型造成浪費。
    if not source_text.strip():
        st.error("請先輸入要處理的資料。")
        return
    if len(source_text) > 12000:
        st.error("輸入文字過長，請先縮短到 12000 字以內，避免成本過高或等待太久。")
        return

    prompt = build_prompt(source_text, task_goal, output_style)

    try:
        with st.spinner("AI 正在處理中..."):
            if use_structured:
                result = extract_structured(prompt)
                render_structured_result(result)
            else:
                result_text = ask_ai(prompt)
                st.subheader("AI 回覆")
                st.write(result_text)
    except RuntimeError as exc:
        st.error(str(exc))
    except Exception as exc:
        # 正式 App 可以把詳細錯誤寫入 log。課堂 starter 只顯示簡短訊息，
        # 避免把環境資訊或 SDK traceback 全部暴露給使用者。
        st.error(f"執行時發生未預期錯誤：{exc}")


if __name__ == "__main__":
    main()
