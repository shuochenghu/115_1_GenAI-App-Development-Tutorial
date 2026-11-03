"""第11週離線驗證：真實SDK＋HTTP模擬；不操作真正平台資源。"""
import ast
from contextlib import redirect_stdout
import hashlib
import importlib.util
from io import StringIO
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch

import httpx
import openai
import streamlit as st
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
WEEK = ROOT / "week11"
PACKAGE = WEEK / "week11_rag_simple"
TEMP = ROOT / "output/week11_simple_revision"
TEMP.mkdir(parents=True, exist_ok=True)
(TEMP / ".gitignore").write_text("*\n", encoding="utf-8")
tempfile.tempdir = str(TEMP.resolve())
SDK_CLIENT = openai.OpenAI
LACK = "根據目前文件，無法確認這個問題。"


def book(teacher):
    ending = "教師版" if teacher else "學生版"
    return json.loads(next(WEEK.glob(f"*課堂簡化版_{ending}.ipynb")).read_text(encoding="utf-8"))


def functions(teacher=True):
    path = PACKAGE / ("teacher" if teacher else "student") / "app.py"
    nodes = [n for n in ast.parse(path.read_text(encoding="utf-8")).body if isinstance(n, ast.FunctionDef)]
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


def error(call, kind=ValueError):
    try:
        call()
    except kind:
        return
    raise AssertionError("沒有拒絕不合格輸入")


def check_books():
    books = [book(False), book(True)]
    assert [c["id"] for c in books[0]["cells"]] == [c["id"] for c in books[1]["cells"]]
    for s, t in zip(books[0]["cells"], books[1]["cells"]):
        if s["id"] not in ["w11s-cover", "w11s-a", "w11s-record"]:
            assert s == t, s["id"]
    for teacher, b in zip([False, True], books):
        assert len(b["cells"]) == len({c["id"] for c in b["cells"]})
        by_tag = {c["id"].removeprefix("w11s-"): c for c in b["cells"]}
        namespace = {}
        for c in b["cells"]:
            source = "".join(c["source"])
            assert "\ufffd" not in source and "???" not in source
            if c["cell_type"] == "markdown":
                headings = re.findall(r"^#{1,6} .+", source, re.M)
                assert not headings or (len(headings) == 1 and source.startswith("#")), c["id"]
                continue
            assert c["execution_count"] is None and c["outputs"] == []
            ast.parse(source)
            with redirect_stdout(StringIO()):
                exec(source, namespace)
            fresh = {}
            for dep in c["metadata"]["teaching"]["requires"]:
                with redirect_stdout(StringIO()):
                    exec("".join(by_tag[dep]["source"]), fresh)
            with redirect_stdout(StringIO()):
                exec(source, fresh)
        assert namespace["self_result"] is None and namespace["fs_result"] is None
        assert namespace["self_error"] is None and namespace["fs_error"] is None
        assert (namespace["context_result"] is not None) == teacher
        assert namespace["text"] == (PACKAGE / "sample_data/activities.txt").read_text(encoding="utf-8")
        ending = "教師版" if teacher else "學生版"
        reading = next(WEEK.glob(f"*課堂簡化版_{ending}.md")).read_text(encoding="utf-8")
        app_tree = ast.parse((PACKAGE / ("teacher" if teacher else "student") / "app.py").read_text(encoding="utf-8"))
        for c in b["cells"]:
            assert "".join(c["source"]) in reading
        for tag, name in [("a", "build_context"), ("answer-fn", "read_answer"), ("retrieve-fn", "retrieve_hits"), ("fs-evidence", "file_search_evidence")]:
            node = ast.parse("".join(by_tag[tag]["source"])).body[0]
            actual = next(n for n in app_tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
            assert ast.dump(node) == ast.dump(actual)
    assert (PACKAGE / "sample_data/activities.txt").read_bytes() == (ROOT / "week10/week10_semantic_search_simple/sample_data/activities.txt").read_bytes()
    print(f"Notebook：雙版各{len(books[0]['cells'])}格，JSON／ID／輸出／AST／先備獨立與順序／答案分離／App與Markdown對齊；兩路與第10週同文件通過")


def check_context():
    fn = functions()["build_context"]
    hits = [{"source": "x.txt", "chunk_id": 4, "text": "  原文4人。 "}, {"source": "x.txt", "chunk_id": 5, "text": "未公告費用"}]
    old = json.loads(json.dumps(hits))
    pack = fn(hits)
    assert hits == old and [h["label"] for h in pack["sources"]] == ["[來源1]", "[來源2]"]
    assert hits[0]["text"] in pack["text"] and "x.txt／4" in pack["text"]
    first = fn(hits[:1])
    assert fn(hits, len(first["text"])) == first
    error(lambda: fn(hits, len(first["text"]) - 1))
    error(lambda: fn(hits, 0))
    error(lambda: fn(hits, True))
    error(lambda: fn([{"source": "x", "chunk_id": 0, "text": " "}]))
    assert fn([]) == {"text": "", "sources": []}
    error(lambda: functions(False)["build_context"](hits), NotImplementedError)
    print("A：完整原文／標籤／來源副本、整段上限、第一段超限與空證據通過")


class Backend:
    """僅供教師測試的HTTP後端；不放進學生App。"""
    def __init__(self):
        self.calls = []
        self.settings = []
        self.mode = "good"
        self.resource_status = "completed"

    def handle(self, request):
        path = request.url.path.removeprefix("/v1")
        content_type = request.headers.get("content-type", "")
        body = json.loads(request.content) if "application/json" in content_type and request.content else None
        self.calls.append((request.method, path, body))
        if self.mode == "timeout":
            raise httpx.ReadTimeout("offline timeout", request=request)
        if self.mode == "429":
            return httpx.Response(429, json={"error": {"message": "offline", "type": "rate_limit_error"}})
        if path == "/embeddings":
            data = [{"object": "embedding", "index": i, "embedding": [1.0, 0.0]} for i in range(len(body["input"]))]
            if self.mode == "no-hits": data[-1]["embedding"] = [0.0, 1.0]
            if self.mode == "bad-vector": data[-1]["embedding"] = [0.0, 0.0]
            return httpx.Response(200, json={"object": "list", "model": body["model"], "data": data, "usage": {"prompt_tokens": 1, "total_tokens": 1}})
        if path == "/responses":
            hosted = bool(body.get("tools"))
            answer = "圖書館討論室。" if hosted else "圖書館討論室。[來源1]"
            if self.mode == "lack" or "火星" in str(body["input"]): answer = LACK
            if self.mode == "bad-label": answer = "圖書館討論室。[來源99]"
            if self.mode == "no-citation": answer = "圖書館討論室。"
            if self.mode == "empty": answer = " "
            annotations = [{"type": "file_citation", "index": 0, "file_id": "file-test", "filename": "activities.txt"}] if hosted else []
            if self.mode in ["no-citation", "no-hits"]: annotations = []
            if self.mode == "wrong-citation": annotations[0]["file_id"] = "file-other"
            output = []
            if hosted and self.mode != "no-tool":
                results = [{"file_id": "file-test", "filename": "activities.txt", "score": 0.9,
                            "text": "工作坊在圖書館討論室舉行。"}]
                if self.mode == "wrong-file": results[0]["file_id"] = "file-other"
                if self.mode == "no-results": results = None
                if self.mode == "no-hits": results, answer = [], LACK
                output.append({"id": "fs_test", "type": "file_search_call", "status": "incomplete" if self.mode == "tool-incomplete" else "completed", "queries": ["地點"], "results": results})
            content = [{"type": "output_text", "text": answer, "annotations": annotations}]
            if self.mode == "refusal": content = [{"type": "refusal", "refusal": "offline refusal"}]
            output.append({"id": "msg_test", "type": "message", "role": "assistant", "status": "completed", "content": content})
            return httpx.Response(200, json={"id": "resp_test", "object": "response", "created_at": 0,
                "model": body["model"], "status": "incomplete" if self.mode == "incomplete" else "completed", "output": output})
        if path == "/vector_stores" and request.method == "POST":
            return httpx.Response(200, json={"id": "vs_test", "object": "vector_store", "created_at": 0, "status": "completed", "name": "week11"})
        if path == "/files" and request.method == "POST":
            return httpx.Response(200, json={"id": "file-test", "object": "file", "bytes": 100, "created_at": 0, "filename": "activities.txt", "purpose": "assistants"})
        if path.endswith("/files") and request.method == "POST":
            if self.mode == "attach-failed":
                return httpx.Response(400, json={"error": {"message": "offline attachment failure", "type": "invalid_request_error"}})
            return httpx.Response(200, json=self.file_status())
        if path.endswith("/files/file-test") and request.method == "GET":
            return httpx.Response(200, json=self.file_status())
        if request.method == "DELETE":
            if self.mode == "cleanup-partial" and path.startswith("/vector_stores"):
                return httpx.Response(500, json={"error": {"message": "offline delete failure", "type": "server_error"}})
            if self.mode == "already-gone":
                return httpx.Response(404, json={"error": {"message": "not found", "type": "invalid_request_error"}})
            return httpx.Response(200, json={"id": path.split("/")[-1], "object": "vector_store.deleted" if "vector_stores" in path else "file", "deleted": True})
        raise AssertionError((request.method, path))

    def file_status(self):
        return {"id": "file-test", "object": "vector_store.file", "created_at": 0,
                "status": self.resource_status, "usage_bytes": 100, "vector_store_id": "vs_test", "last_error": None}

    def client(self, **kwargs):
        self.settings.append({k: kwargs[k] for k in ["max_retries", "timeout"]})
        return SDK_CLIENT(http_client=httpx.Client(transport=httpx.MockTransport(self.handle)), **kwargs)


def check_notebook_api():
    backend = Backend()
    b = book(True)
    by_tag = {c["id"].removeprefix("w11s-"): c for c in b["cells"]}
    def run(tag, mode="good", paid=True, student=False):
        backend.mode = mode
        backend.calls.clear()
        namespace = {}
        deps = by_tag[tag]["metadata"]["teaching"]["requires"]
        for dep in deps:
            text = "".join(by_tag[dep]["source"])
            if dep == "a" and student:
                text = "".join(next(c for c in book(False)["cells"] if c["id"] == "w11s-a")["source"])
            exec(text, namespace)
        source = "".join(by_tag[tag]["source"])
        flag = "RUN_SELF_RAG" if tag == "self-run" else "RUN_FILE_SEARCH"
        source = source.replace(flag + " = False", flag + " = " + str(paid))
        env = {"OPENAI_API_KEY": "offline-placeholder", "OPENAI_VECTOR_STORE_ID": "vs_test", "OPENAI_FILE_ID": "file-test"}
        with patch.object(openai, "OpenAI", backend.client), patch("dotenv.load_dotenv"), patch.dict(os.environ, env), redirect_stdout(StringIO()):
            exec(source, namespace)
        return namespace
    for tag, field in [("self-run", "self_result"), ("fs-run", "fs_result")]:
        assert run(tag, paid=False)[field] is None and not backend.calls
        assert run(tag, student=True)[field] is None and not backend.calls
        result = run(tag)
        assert result[field] and len(backend.calls) == (2 if tag == "self-run" else 1)
        for mode in ["refusal", "incomplete", "empty", "no-citation", "429", "timeout"]:
            assert run(tag, mode)[field] is None, (tag, mode)
        if tag == "self-run":
            assert run(tag, "bad-label")[field] is None
            assert run(tag, "bad-vector")[field] is None
            assert run(tag, "no-hits")[field]["answer"] == LACK and len(backend.calls) == 1
        else:
            for mode in ["wrong-file", "wrong-citation", "no-tool", "no-results", "tool-incomplete"]:
                assert run(tag, mode)[field] is None, mode
            assert run(tag, "no-hits")[field]["answer"] == LACK
            body = backend.calls[0][2]
            assert body["include"] == ["file_search_call.results"] and body["max_tool_calls"] == 1
            assert body["tool_choice"] == {"type": "file_search"} and body["store"] is False
    assert all(s == {"max_retries": 0, "timeout": 60.0} for s in backend.settings)
    print("Notebook API：真實SDK／HTTP模擬驗證兩路0／1／2次、A付費前阻擋、空證據、引用／拒答／未完成／空回應及失敗清舊結果通過")


def check_resources():
    spec = importlib.util.spec_from_file_location("week11_resources_test", PACKAGE / "resources.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    backend = Backend()
    with tempfile.TemporaryDirectory(dir=TEMP) as folder:
        manifest = Path(folder) / "resources.json"
        with patch.object(module, "MANIFEST", manifest), patch.object(module.time, "sleep"), patch.object(module, "OpenAI", backend.client), patch("dotenv.load_dotenv"), patch.dict(os.environ, {"OPENAI_API_KEY": "offline-placeholder"}):
            with redirect_stdout(StringIO()): module.main([])
            assert not backend.calls and not manifest.exists()
            with backend.client(api_key="offline-placeholder", max_retries=0, timeout=60.0) as client:
                data = module.create_resources(client)
                assert data["status"] == "completed" and len(backend.calls) == 4
                assert backend.calls[0][2]["expires_after"] == {"anchor": "last_active_at", "days": 1}
                before = len(backend.calls)
                error(lambda: module.create_resources(client))
                assert len(backend.calls) == before
                backend.mode = "cleanup-partial"
                error(lambda: module.cleanup_resources(client), RuntimeError)
                saved = json.loads(manifest.read_text(encoding="utf-8"))
                assert saved["vector_store_id"] and saved["file_id"] is None and saved["status"] == "cleanup_pending"
                backend.mode = "good"
                assert module.cleanup_resources(client)["status"] == "cleaned"
                backend.mode = "attach-failed"
                error(lambda: module.create_resources(client), openai.BadRequestError)
                saved = json.loads(manifest.read_text(encoding="utf-8"))
                assert saved["vector_store_id"] and saved["file_id"]
                backend.mode = "already-gone"
                assert module.cleanup_resources(client)["status"] == "cleaned"
                backend.mode = "good"
                backend.resource_status = "in_progress"
                backend.calls.clear()
                error(lambda: module.create_resources(client), TimeoutError)
                assert sum(method == "GET" for method, _, _ in backend.calls) == 10
                assert json.loads(manifest.read_text(encoding="utf-8"))["status"] == "in_progress"
                module.cleanup_resources(client)
                backend.resource_status = "failed"
                error(lambda: module.create_resources(client))
                assert json.loads(manifest.read_text(encoding="utf-8"))["status"] == "failed"
                module.cleanup_resources(client)
    print("資源：預設0請求、建立／保存ID／完成狀態／TTL、重複阻擋、10次輪詢上限、附加失敗留ID、部分清理續作與404通過")


def check_apps():
    backend = Backend()
    downloads = []
    def download(label, data, *args, **kwargs):
        downloads.append(json.loads(data))
        return False
    def submit(at):
        downloads.clear()
        at.button[1].click().run()
        assert not at.exception, at.exception
    with tempfile.TemporaryDirectory(dir=TEMP) as folder:
        target = Path(folder)
        for name in ["teacher/app.py", "student/app.py", "sample_data/activities.txt"]:
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((PACKAGE / name).read_bytes())
        manifest = target / ".file_search_resources.json"
        state = {"vector_store_id": "vs_test", "file_id": "file-test", "status": "completed", "sha256": hashlib.sha256((target / "sample_data/activities.txt").read_bytes()).hexdigest()}
        with patch.object(openai, "OpenAI", backend.client), patch.object(st, "secrets", {}), patch.object(st, "download_button", download), patch("dotenv.load_dotenv"), patch.dict(os.environ, {"OPENAI_API_KEY": "offline-placeholder"}):
            at = AppTest.from_file(str(target / "teacher/app.py"), default_timeout=20).run()
            assert not at.exception and not backend.calls
            submit(at)
            assert at.session_state["record"] is None and at.session_state["preview"] and not backend.calls and not downloads
            at.checkbox[0].check().run()
            with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
                submit(at)
                assert at.error and not backend.calls
            submit(at)
            assert len(backend.calls) == 2 and downloads[-1]["route"] == "自行建置"
            first = at.session_state["record"]
            at.run()
            assert len(backend.calls) == 2 and at.session_state["record"] == first
            for mode in ["bad-label", "no-citation", "refusal", "incomplete", "empty", "429", "timeout", "bad-vector"]:
                backend.mode = "good"
                submit(at)
                assert at.session_state["record"]
                backend.mode = mode
                submit(at)
                assert at.error and not downloads and at.session_state["record"] is None, mode
            backend.mode = "no-hits"
            before = len(backend.calls)
            submit(at)
            assert len(backend.calls) == before + 1 and downloads[-1]["generation"].startswith("本機")
            backend.mode = "good"
            at.selectbox[0].select("OpenAI File Search").run()
            before = len(backend.calls)
            submit(at)
            assert at.error and len(backend.calls) == before and not downloads
            manifest.write_text(json.dumps(state), encoding="utf-8")
            submit(at)
            assert len(backend.calls) == before + 1 and downloads[-1]["citations"][0]["file_id"] == "file-test"
            assert downloads[-1]["sha256"] == state["sha256"]
            for mode in ["wrong-file", "wrong-citation", "no-tool", "no-results", "tool-incomplete", "no-citation", "incomplete", "refusal", "empty", "429", "timeout"]:
                backend.mode = "good"
                submit(at)
                assert at.session_state["record"]
                backend.mode = mode
                submit(at)
                assert at.error and not downloads and at.session_state["record"] is None, mode
            backend.mode = "good"
            for field, value in [("status", "in_progress"), ("sha256", "changed")]:
                invalid = dict(state); invalid[field] = value
                manifest.write_text(json.dumps(invalid), encoding="utf-8")
                before = len(backend.calls)
                submit(at)
                assert at.error and not downloads and len(backend.calls) == before
            manifest.write_text(json.dumps(state), encoding="utf-8")
            for q in ["", "A" * 301]:
                at.text_input[0].set_value(q)
                before = len(backend.calls)
                submit(at)
                assert at.error and not downloads and len(backend.calls) == before
            at.text_input[0].set_value("工作坊地點在哪裡？")
            submit(at)
            before = len(backend.calls)
            at.button[0].click().run()
            assert at.session_state["record"] is None and len(backend.calls) == before
            assert not any(path.startswith(("/files", "/vector_stores")) for _, path, _ in backend.calls)
            student = AppTest.from_file(str(target / "student/app.py"), default_timeout=20).run()
            student.checkbox[0].check().run()
            before = len(backend.calls)
            submit(student)
            assert student.error and len(backend.calls) == before
            source = (target / "student/app.py").read_text(encoding="utf-8")
            answer_source = (target / "teacher/app.py").read_text(encoding="utf-8")
            node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "build_context")
            answer = next(n for n in ast.parse(answer_source).body if isinstance(n, ast.FunctionDef) and n.name == "build_context")
            lines = source.splitlines(keepends=True)
            completed = "".join(lines[:node.lineno-1]) + ast.get_source_segment(answer_source, answer) + "\n" + "".join(lines[node.end_lineno:])
            path = target / "student/completed.py"
            path.write_text(completed, encoding="utf-8")
            done = AppTest.from_file(str(path), default_timeout=20).run()
            submit(done)
            assert done.session_state["preview"] and not done.error
    print("AppTest：雙版0請求、只移入A成功、兩路成功與引用失敗、空證據、SHA／索引狀態、切換／清除／rerun與付費前阻擋通過；App不建立資源")


def check_preservation():
    paths = list(WEEK.glob("*課堂簡化版_*.ipynb")) + list(WEEK.glob("*課堂簡化版_*.md")) + [p for p in PACKAGE.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    before = {p: p.read_bytes() for p in paths}
    subprocess.run([sys.executable, "-B", "-X", "utf8", str(ROOT / "scripts/build_week11_simple.py")], check=True, capture_output=True)
    assert all(p.read_bytes() == content for p, content in before.items())
    for p in list(WEEK.glob("*課堂簡化版*.md")) + [PACKAGE / "README.md"]:
        text = p.read_text(encoding="utf-8")
        assert "\ufffd" not in text and "???" not in text and len(re.findall(r"^```", text, re.M)) % 2 == 0
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if not target.startswith(("https://", "http://", "#")):
                assert (p.parent / target.split("#")[0]).exists(), (p, target)
    saved = json.loads((TEMP / "before.json").read_text(encoding="utf-8"))
    for name, checksum in saved["hashes"].items():
        if name == "PROJECT_MEMORY.md": continue
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == checksum, name
    print("重建、相對連結與原有教材／第9～10週未提交成果雜湊保留通過")


def main():
    check_books()
    check_context()
    check_notebook_api()
    check_resources()
    check_apps()
    check_preservation()
    print("全部離線驗證通過；0次真實API、無真正上傳／索引／刪除，未測模型品質、真人瀏覽器、Colab、Cloud或試教。")


if __name__ == "__main__":
    main()
