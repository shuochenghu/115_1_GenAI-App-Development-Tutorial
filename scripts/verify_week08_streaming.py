"""第8週串流範例離線畫面檢查；假SDK不會呼叫網路。"""
import ast
import os
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch
import openai
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "week08/week08_midterm_simple_pydantic_streaming_teacher/app.py"
os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("OPENAI_MODEL", None)
data = {"title": "課程", "summary": "課程介紹表單。", "key_points": ["集中提交"]}
state = {"mode": "ok", "calls": 0, "closed": 0}

class Stream:
    def __init__(self, model):
        self.model = model
    def __enter__(self):
        return self
    def __exit__(self, *args):
        state["closed"] += 1
    def __iter__(self):
        yield NS(type="response.output_text.delta", delta='{"title":')
        if state["mode"] == "disconnect":
            raise ConnectionError("fake disconnect")
        if state["mode"] == "refusal":
            yield NS(type="response.refusal.delta", delta="拒答")
        elif state["mode"] == "incomplete":
            yield NS(type="response.incomplete")
        else:
            yield NS(type="response.output_text.delta", delta='"課程"}')
    def get_final_response(self):
        values = dict(data)
        if state["mode"] == "blank":
            values["title"] = " "
        if state["mode"] == "invalid":
            values["summary"] = 5
        parsed = self.model.model_validate(values)
        return NS(output=[], status="completed", output_text="fake JSON", output_parsed=parsed)

class Client:
    def __init__(self, **kwargs):
        assert kwargs["max_retries"] == 0
        self.responses = self
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def stream(self, **kwargs):
        assert kwargs["store"] is False
        state["calls"] += 1
        return Stream(kwargs["text_format"])

ast.parse(APP.read_text(encoding="utf-8"))
with patch.object(openai, "OpenAI", Client), patch("dotenv.load_dotenv", return_value=False):
    at = AppTest.from_file(str(APP)).run()
    assert not at.exception and state["calls"] == 0
    at.text_area[0].set_value("表單集中提交輸入。")
    at.button[-1].click().run()
    assert state["calls"] == 0 and at.session_state.record is None
    # 用假的Secrets金鑰；不讀取本機真實.env、不建立網路client。
    at.secrets["OPENAI_API_KEY"] = "offline-test"
    at.checkbox[0].check().run()
    at.button[-1].click().run()
    assert not at.exception and at.session_state.record["data"] == data
    calls = state["calls"]
    at.run()
    assert state["calls"] == calls and at.session_state.record
    for mode in ["disconnect", "refusal", "incomplete", "blank", "invalid"]:
        state["mode"] = mode
        at.button[-1].click().run()
        assert not at.exception and at.session_state.record is None and at.error, mode
        assert not at.code, "預覽須在失敗時清除"
    state["mode"] = "ok"
    at.button[-1].click().run()
    at.button[0].click().run()
    assert at.session_state.record is None
    assert state["closed"] == state["calls"]
print("PASS: offline submit, success, rerun, clear, refusal, incomplete, disconnect, blank, Pydantic validation, stream cleanup")
