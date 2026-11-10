"""第13週修訂版離線驗證：真實SDK＋MockTransport與AppTest；0次真實API。"""
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
PACKAGE = WEEK / "week13_web_tools_revised"
TEMP = ROOT / "output/week13_revised_checks"
TEMP.mkdir(parents=True, exist_ok=True)
(TEMP / ".gitignore").write_text("*\n", encoding="utf-8")
tempfile.tempdir = str(TEMP.resolve())
REAL_OPENAI = openai.OpenAI
BUILD = runpy.run_path(str(ROOT / "scripts/build_week13_revised.py"))
PREFIX = "w13r-"
TOPIC = "Streamlit的requirements.txt應放哪裡？"
QUERY = "requirements.txt dependencies"
URL = "https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies"
BOOK_GLOB = "*課堂簡化版_修訂版_{}.ipynb"
# 測試期間不得讀到使用者真實金鑰。
for name in [k for k in os.environ if k.startswith("OPENAI_")]:
    del os.environ[name]


def functions(teacher=True):
    source = (PACKAGE / ("teacher" if teacher else "student") / "app.py").read_text(encoding="utf-8")
    ns = {"st": st}
    tree = ast.parse(source)
    keep = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))]
    exec(BUILD["POLICY"], ns)
    exec(compile(ast.Module(body=keep, type_ignores=[]), "<functions>", "exec"), ns)
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
        path = next(WEEK.glob(BOOK_GLOB.format(ending)))
        b = json.loads(path.read_text(encoding="utf-8"))
        books.append(b)
        assert len(b["cells"]) == len({c["id"] for c in b["cells"]}) == 32
        tags = {c["id"].removeprefix(PREFIX): c for c in b["cells"]}
        namespace = {}
        reading = path.with_suffix(".md").read_text(encoding="utf-8")
        for c in b["cells"]:
            source = "".join(c["source"])
            assert source in reading and "�" not in source and "???" not in source
            if c["cell_type"] == "markdown":
                assert len(re.findall(r"^#{1,6} .+", re.sub(r"```.*?```", "", source, flags=re.S), re.M)) == 1
                assert source.startswith("#")
                continue
            ast.parse(source)
            assert c["outputs"] == [] and c["execution_count"] is None
            # 每個程式格第一行都要讓學生看得到先備
            assert source.startswith("# 先備：") or source.startswith("def build_search_task"), c["id"]
            with redirect_stdout(StringIO()):
                exec(source, namespace)
            fresh = {}
            for dep in c["metadata"]["teaching"]["requires"]:
                with redirect_stdout(StringIO()):
                    exec("".join(tags[dep]["source"]), fresh)
            with redirect_stdout(StringIO()):
                exec(source, fresh)
        assert namespace["first"] is namespace["search_result"] is namespace["direct_result"] is None
        assert namespace["a_checked"] == (ending == "教師版")
        assert (namespace["demo_followup"] is not None) == (ending == "教師版")
        if ending == "教師版":
            last = namespace["demo_followup"][-1]
            assert last["call_id"] == "call_demo_001" and json.loads(last["output"])["query"]
        app = ast.parse((PACKAGE / ("teacher" if ending == "教師版" else "student") / "app.py").read_text(encoding="utf-8"))
        for tag, name in [("a", "build_search_task"), ("call-reader", "read_function_call"),
                          ("url", "allowed_url"), ("url", "page_of"), ("reader", "read_search_result")]:
            node = next(n for n in ast.parse("".join(tags[tag]["source"])).body
                        if isinstance(n, ast.FunctionDef) and n.name == name)
            actual = next(n for n in app.body if isinstance(n, ast.FunctionDef) and n.name == name)
            assert ast.dump(node) == ast.dump(actual), name
    for s, t in zip(books[0]["cells"], books[1]["cells"]):
        if s["id"] not in {PREFIX + "cover", PREFIX + "a", PREFIX + "b"}:
            assert s == t, s["id"]
    assert "教師判讀標準" not in "".join(books[0]["cells"][26]["source"])
    trees = []
    for role in ("student", "teacher"):
        source = (PACKAGE / role / "app.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        assert len([n for n in tree.body if isinstance(n, ast.FunctionDef)]) == 7
        tree.body = [n for n in tree.body if not (isinstance(n, ast.FunctionDef) and n.name == "build_search_task")]
        trees.append(ast.dump(tree))
        if role == "teacher":
            assert "raise NotImplementedError" not in source
    assert trees[0] == trees[1]
    print("PASS Notebook配對／32格／ID／清空輸出／可見先備／AST／先備獨立與順序／Markdown與App對齊")


def first_body(query=QUERY, scope="Streamlit"):
    return {"id": "resp_proposal", "object": "response", "created_at": 0, "model": "offline-model",
            "status": "completed", "parallel_tool_calls": False, "tools": [], "tool_choice": "auto",
            "output": [{"id": "rs_mock", "type": "reasoning", "summary": [], "encrypted_content": "offline-encrypted-placeholder"},
                       {"id": "fc_mock", "type": "function_call", "name": "prepare_search", "call_id": "call_mock",
                        "arguments": json.dumps({"search_query": query, "scope": scope}), "status": "completed"}]}


def search_body():
    answer = "套件清單放在入口同層或Repo根目錄。[1]"
    return {"id": "resp_search", "object": "response", "created_at": 0, "model": "offline-model",
            "status": "completed", "parallel_tool_calls": False, "tools": [], "tool_choice": "auto",
            "output": [{"id": "ws_mock", "type": "web_search_call", "status": "completed",
                        "action": {"type": "search", "query": QUERY, "queries": [QUERY],
                                   "sources": [{"type": "url", "url": URL}]}},
                       {"id": "msg_mock", "type": "message", "role": "assistant", "status": "completed",
                        "content": [{"type": "output_text", "text": answer, "annotations": [
                            {"type": "url_citation", "title": "App dependencies", "url": URL,
                             "start_index": answer.index("[1]"), "end_index": len(answer)}]}]}]}


def set_args(body, value):
    body["output"][1]["arguments"] = value if isinstance(value, str) else json.dumps(value)
    return body


def bad_proposals():
    cases = []
    for status in ("incomplete", "failed", None):
        body = first_body(); body["status"] = status; cases.append(body)
    body = first_body(); body["output"][1]["name"] = "delete_files"; cases.append(body)
    body = first_body(); body["output"][1]["call_id"] = ""; cases.append(body)
    for value in ("not JSON", "[]",
                  {"search_query": QUERY, "scope": "Python"},              # 模型換範圍
                  {"search_query": QUERY, "scope": "Streamlit", "extra": 1},
                  {"search_query": QUERY},
                  {"search_query": "https://docs.streamlit.io", "scope": "Streamlit"},
                  {"search_query": "a" * 81, "scope": "Streamlit"},
                  {"search_query": "  ", "scope": "Streamlit"},
                  {"search_query": "line1\nline2", "scope": "Streamlit"}):
        cases.append(set_args(first_body(), value))
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
    for url in ("https://docs.streamlit.io.evil.example/page", "javascript:alert(1)",
                "https://user:pass@docs.streamlit.io/page", "https://docs.python.org/3/"):
        body = search_body(); body["output"][0]["action"]["sources"][0]["url"] = url; cases.append(body)
    body = search_body(); body["output"][0]["action"]["sources"] = []; cases.append(body)
    body = search_body(); body["output"][1]["content"][0]["annotations"] = []; cases.append(body)
    body = search_body(); body["output"][1]["content"][0]["annotations"][0]["url"] = URL + "/invented"; cases.append(body)
    body = search_body(); body["output"][1]["content"][0]["text"] = " "; cases.append(body)
    body = search_body(); body["output"][1]["content"] = [{"type": "refusal", "refusal": "mock"}]; cases.append(body)
    return cases


def good_search_variants():
    """原版會誤判、修訂版應接受的情況。"""
    variants = []
    body = search_body(); body["output"][1]["content"][0]["annotations"][0]["url"] = URL + "?utm_source=openai"; variants.append(body)
    body = search_body(); body["output"][1]["content"][0]["annotations"][0]["url"] = URL + "#dependencies"; variants.append(body)
    body = search_body(); body["output"][0]["action"]["sources"][0]["url"] = URL + "/"; variants.append(body)
    body = search_body(); note = body["output"][1]["content"][0]["annotations"]
    note.append(copy.deepcopy(note[0])); variants.append(body)                       # 同一段重複引用
    body = search_body(); body["output"][1]["content"][0]["annotations"][0]["title"] = " "; variants.append(body)
    body = search_body(); body["output"].insert(1, {"id": "ws_open", "type": "web_search_call", "status": "completed",
                                                    "action": {"type": "open_page", "url": URL}}); variants.append(body)
    return variants


def check_local_and_http():
    ns = functions()
    build, run = ns["build_search_task"], ns["run_search"]
    assert build("  測試 keyword  ", "Python") == {"query": "測試 keyword", "allowed_domains": ["docs.python.org", "www.python.org"]}
    for query, scope in ((" ", "Python"), ("a" * 81, "Python"), ("x", "Other"), (None, "Python"),
                         ("see www.python.org", "Python"), ("http://x", "Python")):
        rejects(lambda: build(query, scope))
    rejects(lambda: functions(False)["build_search_task"](QUERY, "Streamlit"), NotImplementedError)
    assert ns["allowed_url"]("https://sub.docs.streamlit.io/a", ["docs.streamlit.io"])
    assert ns["page_of"](URL + "/?utm_source=openai#x") == ns["page_of"](URL)
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
    assert result["search_queries"] == [QUERY] and result["task"]["query"] == QUERY
    first_req, second_req = calls
    assert first_req["parallel_tool_calls"] is False and first_req["tools"][0]["strict"] is True
    assert set(first_req["tools"][0]["parameters"]["properties"]) == {"search_query", "scope"}
    assert first_req["include"] == ["reasoning.encrypted_content"]
    assert first_req["tool_choice"] == {"type": "function", "name": "prepare_search"}
    assert json.loads(first_req["input"][0]["content"]) == {"question": TOPIC, "scope": "Streamlit"}
    assert second_req["tool_choice"] == {"type": "web_search"} and second_req["max_tool_calls"] == 1
    assert second_req["include"] == ["web_search_call.action.sources"]
    assert second_req["tools"][0]["filters"]["allowed_domains"] == ["docs.streamlit.io"]
    assert all(c["store"] is False for c in calls)
    assert [item.get("type", item.get("role")) for item in second_req["input"]] == \
        ["user", "reasoning", "function_call", "function_call_output"]
    assert second_req["input"][1]["encrypted_content"] == "offline-encrypted-placeholder"
    output = second_req["input"][-1]
    assert output["call_id"] == "call_mock" and json.loads(output["output"]) == build(QUERY, "Streamlit")
    for case in bad_proposals():
        calls.clear(); state["first"] = case
        rejects(invoke)
        assert len(calls) == 1
    state["first"] = first_body()
    for case in bad_searches():
        calls.clear(); state["second"] = case
        rejects(invoke)
        assert len(calls) == 2
    for case in good_search_variants():
        calls.clear(); state["second"] = case
        result = invoke()
        assert len(result["citations"]) == 1 and len(calls) == 2
    state["second"] = search_body()
    for failure, count in (("first-timeout", 1), ("second-timeout", 2), ("first-429", 1), ("second-429", 2)):
        calls.clear(); state["failure"] = failure
        rejects(invoke, openai.APIError)
        assert len(calls) == count
    state["failure"] = None
    print("PASS A參數檢查、URL同頁比對、真實SDK兩階段／reasoning與call_id、放寬引用比對、1／2次失敗、不重試")
    return state, calls, factory


def check_live_branches_offline(state, calls, factory):
    """打開Notebook旗標，但仍以HTTP模擬驗證真正的請求分支。"""
    book = json.loads(next(WEEK.glob(BOOK_GLOB.format("教師版"))).read_text(encoding="utf-8"))
    code = {c["id"].removeprefix(PREFIX): "".join(c["source"])
            for c in book["cells"] if c["cell_type"] == "code"}
    with patch.dict(os.environ, {"OPENAI_API_KEY": "offline-test-placeholder"}), \
            patch.object(openai, "OpenAI", factory), patch.object(dotenv, "load_dotenv"), \
            redirect_stdout(StringIO()):
        ns = {}
        for tag in ("policy", "a", "call-reader", "url", "reader"):
            exec(code[tag], ns)
        state["first"], state["second"] = first_body(), search_body()
        calls.clear()
        exec(code["first"].replace("RUN_TOOL_STEP = False", "RUN_TOOL_STEP = True"), ns)
        exec(code["second"].replace("RUN_WEB_STEP = False", "RUN_WEB_STEP = True"), ns)
        assert len(calls) == 2 and ns["first"] is not None and ns["search_result"] is not None
        assert ns["task"] == {"query": QUERY, "allowed_domains": ["docs.streamlit.io"]}
        state["first"] = bad_proposals()[0]
        calls.clear()
        exec(code["first"].replace("RUN_TOOL_STEP = False", "RUN_TOOL_STEP = True"), ns)
        exec(code["second"].replace("RUN_WEB_STEP = False", "RUN_WEB_STEP = True"), ns)
        assert len(calls) == 1 and ns["first"] is None and ns["search_result"] is None and ns["search_error"]
        calls.clear()
        exec(code["direct-code"].replace("RUN_DIRECT_SEARCH = False", "RUN_DIRECT_SEARCH = True"), ns)
        assert len(calls) == 1 and ns["direct_result"]["citations"]
        assert calls[0]["input"].startswith("Streamlit Community Cloud") and calls[0]["max_tool_calls"] == 1
        assert calls[0]["tools"][0]["filters"]["allowed_domains"] == ["docs.streamlit.io"]
        # 學生版A未完成：第一階段在付費前停止
        student = json.loads(next(WEEK.glob(BOOK_GLOB.format("學生版"))).read_text(encoding="utf-8"))
        student_a = next("".join(c["source"]) for c in student["cells"] if c["id"] == PREFIX + "a")
        exec(student_a, ns)
        calls.clear()
        exec(code["first"].replace("RUN_TOOL_STEP = False", "RUN_TOOL_STEP = True"), ns)
        assert not calls and ns["first"] is None and "NotImplementedError" in ns["tool_error"]
    state["first"], state["second"] = first_body(), search_body()
    calls.clear()
    print("PASS Notebook開啟兩階段／前次成功後失敗清空／學生A未完成0次／選讀直接搜尋，各請求均為HTTP模擬")


def check_apps(state, calls, factory):
    def clean(at):
        assert not at.exception, [x.message for x in at.exception]

    def submit(at, topic=TOPIC, manual=None):
        at.text_area[0].set_value(topic)
        if manual is not None:
            at.text_input[0].set_value(manual)
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
            # 學生A未完成：離線練習與API模式都只顯示錯誤、0次請求
            at = AppTest.from_file(str(PACKAGE / "student/app.py"), default_timeout=15).run()
            submit(at)
            assert at.error and record(at) is None and not calls
            os.environ["OPENAI_API_KEY"] = "offline-test-placeholder"
            at.checkbox[0].check().run()
            submit(at)
            assert at.error and record(at) is None and not calls
            del os.environ["OPENAI_API_KEY"]
            for path in (PACKAGE / "teacher/app.py", filled):
                calls.clear(); state["first"] = first_body(); state["second"] = search_body()
                at = AppTest.from_file(str(path), default_timeout=15).run()
                # 離線練習：自己扮演模型
                submit(at, manual="st.cache_data")
                assert at.info and not at.error and not calls and record(at) is None
                assert json.loads(at.json[0].value) == {"query": "st.cache_data", "allowed_domains": ["docs.streamlit.io"]}
                submit(at, manual="https://docs.streamlit.io")
                assert at.error and not calls
                at.checkbox[0].check().run()
                for bad in (" ", "文" * 301):
                    submit(at, bad)
                    assert at.error and not calls
                submit(at)
                assert at.error and not calls   # 缺金鑰
                os.environ["OPENAI_API_KEY"] = "offline-test-placeholder"
                os.environ["OPENAI_MODEL"] = "offline-model"
                submit(at)
                assert len(calls) == 2 and record(at)["question"] == TOPIC
                assert record(at)["function_call"]["arguments"] == {"search_query": QUERY, "scope": "Streamlit"}
                assert record(at)["search_queries"] == [QUERY]
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
    print("PASS 雙版AppTest零請求啟動／未完成A／離線練習／缺key／成功／錯誤清舊結果／模式與清除")


def check_rebuild_and_links():
    paths = [*WEEK.glob("*修訂版*.ipynb"), *WEEK.glob("*修訂版*.md"), *PACKAGE.glob("*/app.py")]
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts/build_week13_revised.py")], check=True, capture_output=True)
    assert before == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    for path in PACKAGE.rglob("*.py"):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    docs = [*WEEK.glob("*修訂版*.md"), *PACKAGE.glob("*.md")]
    for path in docs:
        content = path.read_text(encoding="utf-8")
        assert "�" not in content
        assert sum(line.startswith("```") for line in content.splitlines()) % 2 == 0
        prose = re.sub(r"```[^\n]*\n.*?```", "", content, flags=re.S)
        for link in re.findall(r"\]\(([^)]+)\)", prose):
            if "://" not in link and not link.startswith("#"):
                assert (path.parent / link.split("#")[0]).exists(), (path, link)
    print("PASS 重建一致、Python語法、UTF-8、Markdown與本機連結")


def check_dependency_notes():
    """每個用到前面格子變數／函式的程式格，都在格首寫出名稱與出處；出處（含間接）都在先備與requires。"""
    from notebook_cell_notes import check_dependency_notes as check
    total = 0
    for path in sorted(WEEK.glob("*修訂版_*.ipynb")):
        cells = json.loads(path.read_text(encoding="utf-8"))["cells"]
        total += check(cells, PREFIX, BUILD["CELL_NOUNS"], BUILD["TAG_ALIASES"])
    print(f"格首標註：雙版共{total}個程式格，用到前面的變數／函式與模組都寫出出處，出處（含間接）都在先備與requires，先備使用看得懂的格名通過")


def main():
    check_dependency_notes()
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
