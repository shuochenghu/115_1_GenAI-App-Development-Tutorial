"""教師離線驗證：AppTest／假 SDK 不代表真實模型或瀏覽器通過。"""
import argparse
import ast
import copy
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace as NS
from unittest.mock import patch

import dotenv
import openai
import streamlit as st
from streamlit.testing.v1 import AppTest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    student = root / "week08/week08_midterm_simple_starter/app.py"
    teacher = root / "week08/week08_midterm_simple_teacher/app.py"
    schema = {
        "type": "object",
        "properties": {"title": {"type": "string"}, "summary": {"type": "string"},
                       "key_points": {"type": "array", "items": {"type": "string"}}},
        "required": ["title", "summary", "key_points"], "additionalProperties": False,
    }
    good = {"title": "交流", "summary": "將辦交流，報名未定。", "key_points": ["報名未定"]}
    calls = []
    constructions = []
    response = NS(status="completed", output=[], output_text=json.dumps(good))
    fail = False

    class FakeClient:
        def __init__(self, **kwargs):
            constructions.append(kwargs)
            self.responses = self

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def create(self, **kwargs):
            calls.append(kwargs)
            if fail:
                raise RuntimeError("假 SDK 故障")
            return response

    def clean(at):
        assert not at.exception, [item.message for item in at.exception]

    def submit(at, source):
        at.text_area[0].set_value(source)
        at.button[1].click().run()
        clean(at)

    def record(at):
        return at.session_state["record"]

    for file in (student, teacher):
        text = file.read_text(encoding="utf-8")
        ast.parse(text)
        assert len([x for x in ast.walk(ast.parse(text)) if isinstance(x, ast.FunctionDef)]) == 2
        assert "value=False" in text and "store=False" in text
    assert "TODO A" in student.read_text(encoding="utf-8")
    # 教師版可標明對應的學生TODO，但不得留下真正待完成的骨架。
    teacher_text = teacher.read_text(encoding="utf-8")
    assert all("教師提醒（學生TODO" in line for line in teacher_text.splitlines() if "TODO" in line)

    # 真正缺少設定檔的初始啟動；沒有 key 也不呼叫 SDK。
    with patch.object(openai, "OpenAI", FakeClient), patch.object(dotenv, "load_dotenv"):
        for file in (student, teacher):
            at = AppTest.from_file(str(file)).run()
            clean(at)
            assert not at.checkbox[0].value and record(at) is None
            assert not calls and not constructions

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        filled = Path(tmp) / "student_completed.py"
        source = student.read_text(encoding="utf-8")
        source = source.replace('APP_TITLE = ""', 'APP_TITLE = "社團交流整理"')
        source = source.replace('INSTRUCTIONS = ""', 'INSTRUCTIONS = "只依原文整理"')
        source = source.replace("SCHEMA = {}", "SCHEMA = " + repr(schema))
        filled.write_text(source, encoding="utf-8")

        with patch.object(openai, "OpenAI", FakeClient), patch.object(dotenv, "load_dotenv"), \
                patch.object(st, "secrets", {}), patch.dict(os.environ, {}, clear=True):
            # 原學生骨架未完成時，即使開啟 API 也須 0 次請求。
            at = AppTest.from_file(str(student)).run()
            at.checkbox[0].check().run()
            submit(at, "社團要辦交流")
            assert at.error and record(at) is None and not calls

            # 完整教師範例與完成設計的學生版，執行相同成功／失敗規格。
            for file in (teacher, filled):
                calls.clear()
                constructions.clear()
                response = NS(status="completed", output=[], output_text=json.dumps(good))
                at = AppTest.from_file(str(file)).run()
                submit(at, "社團下週舉辦交流，報名方式未定。")
                assert not calls and record(at) is None and at.info
                at.checkbox[0].check().run()
                submit(at, " ")
                assert not calls and at.error
                submit(at, "文" * 6001)
                assert not calls and at.error
                submit(at, "社團交流")
                assert not calls and "OPENAI_API_KEY" in at.error[0].value

                os.environ["OPENAI_API_KEY"] = "offline-test-placeholder"
                os.environ["OPENAI_MODEL"] = "offline-model"
                submit(at, "社團下週舉辦交流，報名方式未定。")
                assert len(calls) == 1 and record(at)["data"] == good
                assert calls[0]["text"]["format"]["strict"] is True
                assert calls[0]["store"] is False and calls[0]["model"] == "offline-model"
                assert constructions[0]["max_retries"] == 0 and constructions[0]["timeout"] == 60.0
                before = len(calls)
                at.run()
                assert len(calls) == before and record(at)["data"] == good
                submit(at, "")
                assert len(calls) == before and record(at) is None

                bad_responses = [
                    NS(status="completed", output=[NS(type="message", content=[NS(type="refusal")])],
                       output_text=json.dumps(good)),
                    NS(status="incomplete", output=[], output_text=json.dumps(good)),
                    NS(status="failed", output=[], output_text=json.dumps(good)),
                    NS(status=None, output=[], output_text=json.dumps(good)),
                    NS(status="completed", output=[], output_text=" "),
                    NS(status="completed", output=[], output_text="not JSON"),
                ]
                for data in [None, [], {}, {**good, "extra": "x"},
                             {**good, "title": 3}, {**good, "summary": " "},
                             {**good, "key_points": "錯誤型別"}, {**good, "key_points": [3]},
                             {**good, "key_points": [" "]}]:
                    bad_responses.append(NS(status="completed", output=[], output_text=json.dumps(data)))
                for bad in bad_responses:
                    response = NS(status="completed", output=[], output_text=json.dumps(good))
                    submit(at, "先成功")
                    assert record(at) is not None
                    response = bad
                    submit(at, "本次失敗")
                    assert record(at) is None and at.error
                fail = True
                submit(at, "服務故障")
                assert record(at) is None and "RuntimeError" in at.error[0].value
                fail = False
                response = NS(status="completed", output=[], output_text=json.dumps({**good, "key_points": []}))
                submit(at, "沒有明確重點")
                assert record(at)["data"]["key_points"] == []
                at.button[0].click().run()
                assert record(at) is None
                response = NS(status="completed", output=[], output_text=json.dumps(good))
                submit(at, "再次成功")
                before = len(calls)
                at.checkbox[0].uncheck().run()
                assert record(at) is None and len(calls) == before
                del os.environ["OPENAI_API_KEY"]
                del os.environ["OPENAI_MODEL"]

            # 不支援的 Schema 必須在請求前擋下，避免型別規格與檢查脫節。
            for bad_schema in [{**schema, "required": ["title"]},
                               {**schema, "additionalProperties": True},
                               {**schema, "properties": {"age": {"type": "integer"}}, "required": ["age"]}]:
                broken = Path(tmp) / "bad_schema.py"
                broken.write_text(source.replace("SCHEMA = " + repr(schema), "SCHEMA = " + repr(bad_schema)), encoding="utf-8")
                at = AppTest.from_file(str(broken)).run()
                at.checkbox[0].check().run()
                before = len(calls)
                submit(at, "正常原文")
                assert len(calls) == before and record(at) is None and at.error

    print("PASS: syntax, student/teacher separation, zero-request launch, offline guards, missing key,")
    print("      fake SDK request contract, completed/refusal/failure/empty/JSON/field checks,")
    print("      rerun persistence, clear/mode reset, failed submission clears old result, schema guards.")
    import importlib.metadata as md
    import sys
    print("Runtime:", sys.version.split()[0], {n: md.version(n) for n in ["streamlit", "openai", "python-dotenv"]})
    print("Not tested: real API, browser, other-platform installation, Cloud, Colab, classroom duration.")


if __name__ == "__main__":
    main()
