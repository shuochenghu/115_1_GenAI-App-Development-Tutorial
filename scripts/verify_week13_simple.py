"""第13週離線驗證：真實SDK＋MockTransport與AppTest；0次真實API。"""
import ast
from contextlib import redirect_stdout
import copy
import hashlib
from io import StringIO
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import tempfile
from unittest.mock import patch

import dotenv
import httpx
import openai
import streamlit as st
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
WEEK = ROOT / "week13"
PACKAGE = WEEK / "week13_web_tools_simple"
TEMP = ROOT / "output/week13_simple_checks"
TEMP.mkdir(parents=True, exist_ok=True)
(TEMP / ".gitignore").write_text("*\n", encoding="utf-8")
tempfile.tempdir = str(TEMP.resolve())
REAL_OPENAI = openai.OpenAI
BUILD = runpy.run_path(str(ROOT / "scripts/build_week13_simple.py"))
TOPIC = "Streamlit的requirements.txt應放哪裡？"
URL = "https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies"


def functions(teacher=True):
    source = (PACKAGE / ("teacher" if teacher else "student") / "app.py").read_text(encoding="utf-8")
    ns = {"st": st}
    exec(BUILD["IMPORTS"] + "\n" + BUILD["POLICY"], ns)
    nodes = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "<functions>", "exec"), ns)
    return ns


def rejects(call, kind=ValueError):
    try:
        call()
    except kind:
        return
    raise AssertionError("未拒絕不合格資料")


def check_books():
    books = []
    for ending in ("學生版", "教師版"):
        path = next(WEEK.glob(f"*課堂簡化版_{ending}.ipynb"))
        b = json.loads(path.read_text(encoding="utf-8"))
        books.append(b)
        assert len(b["cells"]) == len({c["id"] for c in b["cells"]}) == 26
        tags = {c["id"].removeprefix("w13s-"): c for c in b["cells"]}
        namespace = {}
        reading = path.with_suffix(".md").read_text(encoding="utf-8")
        for c in b["cells"]:
            source = "".join(c["source"])
            assert source in reading and "\ufffd" not in source and "???" not in source
            if c["cell_type"] == "markdown":
                assert len(re.findall(r"^#{1,6} .+", source, re.M)) == 1 and source.startswith("#")
                continue
            ast.parse(source)
            assert c["outputs"] == [] and c["execution_count"] is None
            with redirect_stdout(StringIO()):
                exec(source, namespace)
            fresh = {}
            for dep in c["metadata"]["teaching"]["requires"]:
                with redirect_stdout(StringIO()):
                    exec("".join(tags[dep]["source"]), fresh)
            with redirect_stdout(StringIO()):
                exec(source, fresh)
        assert namespace["first"] is namespace["search_result"] is namespace["direct_result"] is None
        assert (namespace["task_preview"] is not None) == (ending == "教師版")
        app = ast.parse((PACKAGE / ("teacher" if ending == "教師版" else "student") / "app.py").read_text(encoding="utf-8"))
        for tag, name in [("a", "build_search_task"), ("call-reader", "read_function_call"),
                          ("url", "allowed_url"), ("reader", "read_search_result")]:
            node = next(n for n in ast.parse("".join(tags[tag]["source"])).body if isinstance(n, ast.FunctionDef))
            actual = next(n for n in app.body if isinstance(n, ast.FunctionDef) and n.name == name)
            assert ast.dump(node) == ast.dump(actual)
    for s, t in zip(books[0]["cells"], books[1]["cells"]):
        if s["id"] not in {"w13s-cover", "w13s-a"}:
            assert s == t, s["id"]
    # 除A外的App AST一致；教師沒有學生的未完成骨架。
    trees = []
    for role in ("student", "teacher"):
        source = (PACKAGE / role / "app.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        assert len([n for n in tree.body if isinstance(n, ast.FunctionDef)]) == 6
        tree.body = [n for n in tree.body if not (isinstance(n, ast.FunctionDef) and n.name == "build_search_task")]
        trees.append(ast.dump(tree))
        if role == "teacher":
            assert "raise NotImplementedError" not in source
    assert trees[0] == trees[1]
    print("PASS Notebook配對／26格／ID／清空輸出／AST／先備獨立與順序／Markdown與App對齊")


def first_body(topic=TOPIC, scope="Streamlit"):
    return {"id": "resp_proposal", "object": "response", "created_at": 0, "model": "offline-model",
            "status": "completed", "parallel_tool_calls": False, "tools": [], "tool_choice": "auto",
            "output": [{"id": "rs_mock", "type": "reasoning", "summary": [], "encrypted_content": "offline-encrypted-placeholder"},
                       {"id": "fc_mock", "type": "function_call", "name": "prepare_search", "call_id": "call_mock",
                        "arguments": json.dumps({"topic": topic, "scope": scope}, ensure_ascii=False), "status": "completed"}]}


def search_body():
    answer = "套件清單放在入口同層或Repo根目錄。[1]"
    return {"id": "resp_search", "object": "response", "created_at": 0, "model": "offline-model",
            "status": "completed", "parallel_tool_calls": False, "tools": [], "tool_choice": "auto",
            "output": [{"id": "ws_mock", "type": "web_search_call", "status": "completed",
                        "action": {"type": "search", "queries": [TOPIC], "sources": [{"type": "url", "url": URL}]}},
                       {"id": "msg_mock", "type": "message", "role": "assistant", "status": "completed",
                        "content": [{"type": "output_text", "text": answer, "annotations": [
                            {"type": "url_citation", "title": "App dependencies", "url": URL,
                             "start_index": answer.index("[1]"), "end_index": len(answer)}]}]}]}


def bad_proposals():
    cases = []
    for status in ("incomplete", "failed", None):
        body = first_body(); body["status"] = status; cases.append(body)
    for name, value in (("name", "delete_files"), ("call_id", ""), ("arguments", "not JSON"),
                        ("arguments", json.dumps({"topic": TOPIC, "scope": "Python"})),
                        ("arguments", json.dumps({"topic": TOPIC, "scope": "Streamlit", "extra": 1}))):
        body = first_body(); body["output"][1][name] = value; cases.append(body)
    body = first_body(); body["output"].append(copy.deepcopy(body["output"][1])); cases.append(body)
    body = first_body(); body["output"] = []; cases.append(body)
    body = first_body(); body["output"].append({"id": "refusal", "type": "message", "role": "assistant",
                                              "status": "completed", "content": [{"type": "refusal", "refusal": "mock"}]}); cases.append(body)
    return cases


def bad_searches():
    cases = []
    for status in ("incomplete", "failed", None):
        body = search_body(); body["status"] = status; cases.append(body)
    body = search_body(); body["output"][0]["status"] = "failed"; cases.append(body)
    body = search_body(); body["output"] = body["output"][1:]; cases.append(body)
    body = search_body(); body["output"].append(copy.deepcopy(body["output"][0])); cases.append(body)
    for url in ("https://docs.streamlit.io.evil.example/page", "javascript:alert(1)",
                "https://user:pass@docs.streamlit.io/page", "https://docs.python.org/3/"):
        body = search_body(); body["output"][0]["action"]["sources"][0]["url"] = url; cases.append(body)
    body = search_body(); body["output"][0]["action"]["sources"] = []; cases.append(body)
    body = search_body(); body["output"][1]["content"][0]["annotations"] = []; cases.append(body)
    body = search_body(); body["output"][1]["content"][0]["annotations"][0]["url"] = URL + "/invented"; cases.append(body)
    body = search_body(); body["output"][1]["content"][0]["annotations"][0]["title"] = " "; cases.append(body)
    body = search_body(); body["output"][1]["content"][0]["annotations"][0]["end_index"] = 9999; cases.append(body)
    body = search_body(); body["output"][1]["content"][0]["text"] = " "; cases.append(body)
    body = search_body(); body["output"][1]["content"] = [{"type": "refusal", "refusal": "mock"}]; cases.append(body)
    return cases


def check_local_and_http():
    ns = functions()
    build, run = ns["build_search_task"], ns["run_search"]
    assert build("  測試  ", "Python") == {"query": "測試", "allowed_domains": ["docs.python.org", "www.python.org"]}
    for topic, scope in ((" ", "Python"), ("文" * 301, "Python"), ("測試", "Other")):
        rejects(lambda: build(topic, scope))
    rejects(lambda: functions(False)["build_search_task"](TOPIC, "Streamlit"), NotImplementedError)
    assert ns["allowed_url"]("https://sub.docs.streamlit.io/a", ["docs.streamlit.io"])
    calls = []
    state = {"first": first_body(), "second": search_body(), "failure": None}

    def handler(request):
        data = json.loads(request.content)
        calls.append(data)
        assert str(request.url) == "https://offline.invalid/v1/responses"
        stage = "first" if data["tools"][0]["type"] == "function" else "second"
        if state["failure"] == stage + "-timeout":
            raise httpx.ReadTimeout("mock", request=request)
        if state["failure"] == stage + "-429":
            return httpx.Response(429, json={"error": {"message": "mock", "type": "rate_limit_error"}})
        return httpx.Response(200, json=copy.deepcopy(state[stage]))

    def factory(**kwargs):
        assert kwargs["max_retries"] == 0 and kwargs["timeout"] == 60.0
        return REAL_OPENAI(**kwargs, base_url="https://offline.invalid/v1",
                           http_client=httpx.Client(transport=httpx.MockTransport(handler)))

    def invoke():
        with factory(api_key="offline-test-placeholder", max_retries=0, timeout=60.0) as client:
            return run(client, TOPIC, "Streamlit", "offline-model")

    result = invoke()
    assert len(calls) == 2 and result["citations"][0]["url"] == URL and result["publication_date"] is None
    assert calls[0]["parallel_tool_calls"] is False and calls[0]["tools"][0]["strict"] is True
    assert calls[0]["include"] == ["reasoning.encrypted_content"]
    assert "[來源1](<" + URL + ">)" in result["answer_with_citations"]
    assert calls[0]["tool_choice"] == {"type": "function", "name": "prepare_search"}
    assert calls[1]["tool_choice"] == {"type": "web_search"} and calls[1]["max_tool_calls"] == 1
    assert calls[1]["include"] == ["web_search_call.action.sources"]
    assert calls[1]["tools"][0]["filters"]["allowed_domains"] == ["docs.streamlit.io"]
    assert all(c["store"] is False for c in calls)
    assert calls[1]["input"][1]["type"] == "reasoning"
    assert calls[1]["input"][1]["encrypted_content"] == "offline-encrypted-placeholder"
    output = calls[1]["input"][-1]
    assert output["type"] == "function_call_output" and output["call_id"] == "call_mock"
    assert json.loads(output["output"]) == build(TOPIC, "Streamlit")
    for case in bad_proposals():
        calls.clear(); state["first"] = case
        rejects(invoke)
        assert len(calls) == 1
    state["first"] = first_body()
    for case in bad_searches():
        calls.clear(); state["second"] = case
        rejects(invoke)
        assert len(calls) == 2
    state["second"] = search_body()
    # 同一頁不同錨點可接受；不可因此放過不同路徑。
    state["second"]["output"][1]["content"][0]["annotations"][0]["url"] += "#dependencies"
    invoke()
    state["second"] = search_body()
    for failure, count in (("first-timeout", 1), ("second-timeout", 2), ("first-429", 1), ("second-429", 2)):
        calls.clear(); state["failure"] = failure
        rejects(invoke, openai.APIError)
        assert len(calls) == count
    state["failure"] = None
    print("PASS 本機A與URL界線、真實SDK兩階段／reasoning與call_id、引用、1／2次失敗、不重試")
    return state, calls, factory


def check_live_branches_offline(state, calls, factory):
    """打開Notebook旗標，但仍以HTTP模擬驗證真正的請求分支。"""
    book = json.loads(next(WEEK.glob("*課堂簡化版_教師版.ipynb")).read_text(encoding="utf-8"))
    code = {c["id"].removeprefix("w13s-"): "".join(c["source"])
            for c in book["cells"] if c["cell_type"] == "code"}
    with patch.dict(os.environ, {"OPENAI_API_KEY": "offline-test-placeholder"}), \
            patch.object(openai, "OpenAI", factory), patch.object(dotenv, "load_dotenv"), \
            redirect_stdout(StringIO()):
        ns = {}
        for tag in ("policy", "a", "call-reader", "url", "reader"):
            exec(code[tag], ns)
        notebook_topic = "Streamlit Community Cloud部署時requirements.txt應放哪裡？"
        state["first"] = first_body(notebook_topic)
        calls.clear()
        exec(code["first"].replace("RUN_TOOL_STEP = False", "RUN_TOOL_STEP = True"), ns)
        exec(code["second"].replace("RUN_WEB_STEP = False", "RUN_WEB_STEP = True"), ns)
        assert len(calls) == 2 and ns["first"] is not None and ns["search_result"] is not None
        state["first"] = bad_proposals()[0]
        calls.clear()
        exec(code["first"].replace("RUN_TOOL_STEP = False", "RUN_TOOL_STEP = True"), ns)
        exec(code["second"].replace("RUN_WEB_STEP = False", "RUN_WEB_STEP = True"), ns)
        assert len(calls) == 1 and ns["first"] is None and ns["search_result"] is None
        calls.clear()
        exec(code["direct-code"].replace("RUN_DIRECT_SEARCH = False", "RUN_DIRECT_SEARCH = True"), ns)
        assert len(calls) == 1 and ns["direct_result"]["citations"]
        assert calls[0]["input"] == TOPIC and calls[0]["max_tool_calls"] == 1
        assert calls[0]["tools"][0]["filters"]["allowed_domains"] == ["docs.streamlit.io"]
    state["first"] = first_body()
    calls.clear()
    print("PASS Notebook開啟兩階段／前次成功後失敗清空／選讀直接搜尋，各請求均為HTTP模擬")


def check_apps(state, calls, factory):
    def clean(at):
        assert not at.exception, [x.message for x in at.exception]

    def submit(at, topic=TOPIC):
        at.text_area[0].set_value(topic)
        at.button[1].click().run()
        clean(at)

    def record(at):
        return at.session_state["record"]

    source = (PACKAGE / "student/app.py").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(dir=TEMP) as tmp:
        filled = Path(tmp) / "student_completed.py"
        assert BUILD["A_STUDENT"] in source
        filled.write_text(source.replace(BUILD["A_STUDENT"], BUILD["A_TEACHER"]), encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if not k.startswith("OPENAI_")}
        with patch.object(openai, "OpenAI", factory), patch.object(dotenv, "load_dotenv"), \
                patch.object(st, "secrets", {}), patch.dict(os.environ, env, clear=True):
            for path in (PACKAGE / "student/app.py", PACKAGE / "teacher/app.py"):
                calls.clear()
                at = AppTest.from_file(str(path), default_timeout=15).run()
                clean(at)
                assert not at.checkbox[0].value and record(at) is None and not calls
            at = AppTest.from_file(str(PACKAGE / "student/app.py"), default_timeout=15).run()
            at.checkbox[0].check().run()
            submit(at)
            assert at.error and record(at) is None and not calls
            for path in (PACKAGE / "teacher/app.py", filled):
                calls.clear(); state["first"] = first_body(); state["second"] = search_body()
                at = AppTest.from_file(str(path), default_timeout=15).run()
                submit(at)
                assert at.info and not calls and record(at) is None
                at.checkbox[0].check().run()
                for bad in (" ", "文" * 301):
                    submit(at, bad)
                    assert at.error and not calls
                submit(at)
                assert at.error and not calls
                os.environ["OPENAI_API_KEY"] = "offline-test-placeholder"
                os.environ["OPENAI_MODEL"] = "offline-model"
                submit(at)
                assert len(calls) == 2 and record(at)["question"] == TOPIC
                assert record(at)["function_call"]["arguments"] == {"topic": TOPIC, "scope": "Streamlit"}
                before = len(calls)
                at.run()
                assert len(calls) == before and record(at) is not None
                for stage, cases in (("first", bad_proposals()), ("second", bad_searches())):
                    for case in cases:
                        state["first"] = first_body(); state["second"] = search_body()
                        submit(at)
                        assert record(at) is not None
                        state[stage] = case
                        before = len(calls)
                        submit(at)
                        assert record(at) is None and at.error
                        assert len(calls) - before == (1 if stage == "first" else 2)
                state["first"] = first_body(); state["second"] = search_body()
                submit(at)
                before = len(calls)
                at.button[0].click().run()
                assert record(at) is None and len(calls) == before
                submit(at)
                before = len(calls)
                at.selectbox[0].select("Python").run()
                assert record(at) is None and len(calls) == before
                at.selectbox[0].select("Streamlit").run()
                submit(at)
                at.checkbox[0].uncheck().run()
                assert record(at) is None
                del os.environ["OPENAI_API_KEY"]
                del os.environ["OPENAI_MODEL"]
    print("PASS 雙版AppTest零請求啟動／未完成A／離線／缺key／成功／錯誤清舊結果／模式與清除")


def check_rebuild_and_links():
    paths = [*WEEK.glob("*.ipynb"), *WEEK.glob("*.md"), *PACKAGE.glob("*/app.py")]
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts/build_week13_simple.py")], check=True, capture_output=True)
    assert before == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    for path in WEEK.rglob("*.py"):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    for path in WEEK.rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        assert "\ufffd" not in content
        assert sum(line.startswith("```") for line in content.splitlines()) % 2 == 0
        prose = re.sub(r"```[^\n]*\n.*?```", "", content, flags=re.S)
        for link in re.findall(r"\]\(([^)]+)\)", prose):
            if "://" not in link and not link.startswith("#"):
                assert (path.parent / link.split("#")[0]).exists(), (path, link)
    print("PASS 重建一致、Python語法、UTF-8、Markdown與本機連結")


def main():
    check_books()
    state, calls, factory = check_local_and_http()
    check_live_branches_offline(state, calls, factory)
    check_apps(state, calls, factory)
    check_rebuild_and_links()
    import importlib.metadata as md
    print("Runtime:", sys.version.split()[0], {n: md.version(n) for n in ("streamlit", "openai", "python-dotenv", "httpx")})
    print("0 real API. Not tested: live web search/citations/model access/billing, browser, Cloud, Colab, classroom duration.")


if __name__ == "__main__":
    main()
