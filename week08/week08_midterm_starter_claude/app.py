"""
Week 8 期中個人小專題 — Starter（Claude 版）

這是一個「可以直接執行的骨架」：
    streamlit run app.py
就能看到畫面，但裡面的專題名稱、AI 任務與輸出欄位都是通用範本。
請依照程式中的 TODO，改造成你自己的期中小專題。

helper 命名對齊第 7 週課堂使用的版本（Codex 版 week07_streamlit_app）：
    get_secret() / create_client() / ask_ai() / stream_ai()
另外新增第 6 週學到的結構化輸出，改用 Pydantic：
    extract_structured() + client.responses.parse() + response.output_parsed
"""

import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
import streamlit as st


# 頁面設定必須在其他 Streamlit 元件之前執行。
st.set_page_config(
    page_title="Week 8 Midterm Starter (Claude)",
    page_icon="🧩",
    layout="centered",
)


# ─────────────────────────────────────────────────────────────
# 一、專題設定：先完成這三個 TODO
# 建議先想清楚「使用者是誰、要解決什麼問題、AI 不該做什麼」，
# 後面的 prompt、schema 與 UI 才會有一致方向。
# ─────────────────────────────────────────────────────────────
PROJECT_TITLE = "TODO：請填入你的期中小專題名稱"
PROJECT_DESCRIPTION = "TODO：請用一句話說明這個 App 解決什麼問題"
SYSTEM_PROMPT = """TODO：請改寫成你的 App 專用 system prompt。

建議包含：
1. AI 扮演什麼角色。
2. 使用者會提供什麼資料。
3. AI 應該輸出什麼內容。
4. 資訊不足時要如何回答，不可捏造。
"""


# ─────────────────────────────────────────────────────────────
# 二、結構化輸出：用 Pydantic 定義欄位（第 6 週技能）
# 用 class 定義欄位的好處是「型別即文件」：欄位名稱、型態與說明
# 一次寫清楚，程式後續可用 result.summary 這種方式安全取值。
# TODO：把下面欄位改成你的專題真正需要的欄位。
# ─────────────────────────────────────────────────────────────
class ProjectResult(BaseModel):
    """期中專題的結構化輸出範本，請依你的題目調整。"""

    title: str = Field(description="本次結果的短標題")
    summary: str = Field(description="用 2 到 3 句話說明 AI 的主要判斷")
    key_points: list[str] = Field(description="最重要的 3 到 5 個重點")
    next_steps: list[str] = Field(description="給使用者的後續行動建議")


# ─────────────────────────────────────────────────────────────
# 三、helper 函式（對齊第 7 週 week07_streamlit_app）
# ─────────────────────────────────────────────────────────────
def get_secret(name, default=None):
    """先讀 Streamlit Secrets（雲端），本機開發時再改讀 .env。"""
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        # 本機直接執行時可能沒有 secrets.toml，忽略即可，改用 .env。
        pass
    load_dotenv()
    return os.getenv(name, default)


def create_client():
    """建立 OpenAI client，缺少 API key 時立刻給出明確錯誤（fail-fast）。"""
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("找不到 OPENAI_API_KEY，請設定 .env 或 Streamlit Secrets。")
    return OpenAI(api_key=api_key)


def ask_ai(user_input, system_prompt=SYSTEM_PROMPT):
    """非串流版本：適合摘要、改寫、建議等一次性文字任務。"""
    client = create_client()
    model = get_secret("OPENAI_MODEL", "gpt-5.4-mini")
    response = client.responses.create(
        model=model,
        instructions=system_prompt,
        input=user_input,
    )
    if not response.output_text:
        raise RuntimeError("AI 沒有回傳文字，請檢查 prompt 或稍後再試。")
    return response.output_text


def stream_ai(user_input, system_prompt=SYSTEM_PROMPT):
    """串流版本（加分項）：逐段 yield 文字，交給 st.write_stream() 顯示。"""
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


def extract_structured(user_input, schema_model=ProjectResult, system_prompt=SYSTEM_PROMPT):
    """
    結構化輸出：要求模型依 Pydantic 模型回傳，並自動解析成物件。

    這裡用 client.responses.parse() 搭配 text_format=Pydantic 模型，
    回傳的 response.output_parsed 會是一個已驗證的 Python 物件，
    可以直接用 result.summary、result.key_points 取值，不需自己 json.loads。

    參數:
        user_input: 要分析的完整 prompt。
        schema_model: Pydantic 模型類別，定義要回傳的欄位。
        system_prompt: 控制 AI 角色、任務規則與限制的系統指令。

    回傳:
        schema_model 的實例（已通過欄位驗證）。
    """
    client = create_client()
    model = get_secret("OPENAI_MODEL", "gpt-5.4-mini")
    response = client.responses.parse(
        model=model,
        instructions=system_prompt,
        input=user_input,
        text_format=schema_model,
    )
    result = response.output_parsed
    if result is None:
        raise RuntimeError("AI 沒有回傳可解析的結構化結果，請檢查 schema 或 prompt。")
    return result


# ─────────────────────────────────────────────────────────────
# 四、prompt 組裝與畫面
# ─────────────────────────────────────────────────────────────
def build_prompt(source_text, task_goal, output_style):
    """把使用者表單輸入整理成一段清楚的 prompt。

    prompt 建議集中在這個函式組裝，不要散在 UI 裡；
    未來要改欄位、測 prompt 或做版本紀錄時只改這裡即可。
    TODO：依你的專題重新設計，建議保留「任務／輸入／限制／輸出」四段。
    """
    return f"""請根據下列資料完成任務。

任務目標：
{task_goal}

輸出風格：
{output_style}

使用者提供的資料：
{source_text}

請勿捏造原文沒有的事實；若資訊不足，請明確說明不足之處。
"""


def render_project_form():
    """顯示主要輸入表單，回傳使用者填寫內容。

    表單適合固定任務：填完欄位按一次送出才呼叫 API，比每次改欄位都
    rerun 呼叫 API 更能控制成本。
    TODO：依你的專題修改欄位名稱與提示文字。
    """
    with st.form("midterm_form"):
        source_text = st.text_area(
            "輸入資料",
            height=220,
            placeholder="貼上要分析、摘要、分類或改寫的文字。",
        )
        task_goal = st.text_input("任務目標", value="TODO：描述你希望 AI 完成的任務")
        output_style = st.selectbox(
            "輸出風格",
            ["條列重點", "給初學者看的說明", "給主管看的摘要", "正式報告語氣"],
        )
        use_structured = st.toggle("使用結構化輸出（建議開啟）", value=True)
        submitted = st.form_submit_button("產生結果")
    return source_text, task_goal, output_style, use_structured, submitted


def render_structured_result(result):
    """把結構化結果轉成好讀的畫面，而不是直接丟一坨 JSON 給使用者。

    參數:
        result: ProjectResult（或你自訂的 Pydantic 模型）實例。
    """
    st.subheader(result.title)
    st.write(result.summary)

    st.markdown("#### 重點")
    for item in result.key_points:
        st.markdown(f"- {item}")

    st.markdown("#### 後續建議")
    for item in result.next_steps:
        st.markdown(f"- {item}")

    with st.expander("查看原始 JSON"):
        # Pydantic 物件可用 model_dump() 轉成 dict 再給 st.json 顯示。
        st.json(result.model_dump())


# ─────────────────────────────────────────────────────────────
# 五、主流程
# ─────────────────────────────────────────────────────────────
def main():
    st.title(PROJECT_TITLE)
    st.caption(PROJECT_DESCRIPTION)

    with st.sidebar:
        st.header("專題檢核")
        st.markdown("- 已設定 App 名稱與說明")
        st.markdown("- 已設計 system prompt")
        st.markdown("- 已設計結構化輸出欄位")
        st.markdown("- 已完成 README")
        st.markdown("- 已確認 API key 不會上傳 GitHub")
        st.divider()
        # 安全紅線：課程反覆強調，也是 rubric 的一票否決項。
        st.error("紅線：API key 只能放 .env 或 Secrets，絕不可寫死或推上 GitHub。")

    # 不顯示 key 內容，只提醒是否已設定。
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
        st.error("輸入文字過長，請縮短到 12000 字以內，避免成本過高或等待太久。")
        return

    prompt = build_prompt(source_text, task_goal, output_style)

    try:
        with st.spinner("AI 正在處理中..."):
            if use_structured:
                result = extract_structured(prompt)
                render_structured_result(result)
            else:
                st.subheader("AI 回覆")
                st.write(ask_ai(prompt))
    except RuntimeError as exc:
        # 已知錯誤（缺 key、空回覆）用簡短訊息提示。
        st.error(str(exc))
    except Exception as exc:
        # 未預期錯誤只顯示簡短訊息，避免把 SDK traceback 全部暴露給使用者。
        st.error(f"執行時發生未預期錯誤：{exc}")


if __name__ == "__main__":
    main()
