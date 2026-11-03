"""第10週簡化版離線驗證；真實SDK＋MockTransport，不送出網路請求。"""
import ast
from contextlib import redirect_stdout
import hashlib
from io import StringIO
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from unittest.mock import patch

import httpx
import openai
import streamlit as st
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
WEEK = ROOT / "week10"
PACKAGE = WEEK / "week10_semantic_search_simple"
TEMP = ROOT / "output/week10_simple_revision"
TEMP.mkdir(parents=True, exist_ok=True)
(TEMP / ".gitignore").write_text("*\n", encoding="utf-8")
tempfile.tempdir = str(TEMP.resolve())
REAL_OPENAI = openai.OpenAI


def read_book(teacher):
    ending = "教師版" if teacher else "學生版"
    return json.loads(next(WEEK.glob(f"*課堂簡化版_{ending}.ipynb")).read_text(encoding="utf-8"))


def functions(teacher):
    path = PACKAGE / ("teacher" if teacher else "student") / "app.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


def error(call, kind=ValueError):
    try:
        call()
    except kind:
        return
    raise AssertionError("未拒絕錯誤輸入")


def check_notebooks():
    books = [read_book(False), read_book(True)]
    assert [c["id"] for c in books[0]["cells"]] == [c["id"] for c in books[1]["cells"]]
    for s, t in zip(books[0]["cells"], books[1]["cells"]):
        if s["id"] not in ["w10s-cover", "w10s-a", "w10s-b-reference"]:
            assert s == t, s["id"]
    for teacher, book in zip([False, True], books):
        cells = book["cells"]
        assert len(cells) == len({c["id"] for c in cells})
        by_id = {c["id"].removeprefix("w10s-"): c for c in cells}
        namespace = {}
        for cell in cells:
            text = "".join(cell["source"])
            assert "\ufffd" not in text and "???" not in text
            if cell["cell_type"] == "markdown":
                headings = re.findall(r"^#{1,6} .+", text, re.M)
                assert not headings or (len(headings) == 1 and text.startswith("#")), cell["id"]
                continue
            assert cell["outputs"] == [] and cell["execution_count"] is None
            ast.parse(text)
            with redirect_stdout(StringIO()):
                exec(text, namespace)
            fresh = {}
            for dependency in cell["metadata"]["teaching"]["requires"]:
                with redirect_stdout(StringIO()):
                    exec("".join(by_id[dependency]["source"]), fresh)
            with redirect_stdout(StringIO()):
                exec(text, fresh)
        assert namespace["embedding_result"] is None and namespace["embedding_error"] is None
        assert (namespace["hits_result"] is not None) == teacher
        assert (namespace["offline_hits"] is not None) == teacher
        assert ("raise NotImplementedError" in "".join(by_id["a"]["source"])) != teacher
        ending = "教師版" if teacher else "學生版"
        reading = next(WEEK.glob(f"*課堂簡化版_{ending}.md")).read_text(encoding="utf-8")
        for cell in cells:
            assert "".join(cell["source"]) in reading
        app_tree = ast.parse((PACKAGE / ("teacher" if teacher else "student") / "app.py").read_text(encoding="utf-8"))
        for tag, name in [("a", "rank_chunks"), ("cosine-fn", "cosine_similarity"), ("demo-fn", "demo_vector")]:
            node = ast.parse("".join(by_id[tag]["source"])).body[0]
            actual = next(n for n in app_tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
            assert ast.dump(node) == ast.dump(actual)
    print(f"Notebook：雙版各{len(books[0]['cells'])}格，JSON／ID／清空輸出／AST／章節／先備獨立與順序／答案分離／Markdown與App對齊通過")


def check_ranking():
    ns = functions(True)
    cosine, rank, demo = [ns[name] for name in ["cosine_similarity", "rank_chunks", "demo_vector"]]
    assert cosine([1, 0], [5, 0]) == 1
    assert cosine([1, 0], [-1, 0]) == -1
    assert cosine([1, 0], [0, 1]) == 0
    assert cosine([0, 0], [1, 0]) == 0
    for a, b in [([], []), ([1], [1, 2]), ([math.nan], [1]), ([math.inf], [1]), ([True], [1])]:
        error(lambda: cosine(a, b))
    chunks = [{"chunk_id": i, "source": "原文.txt", "start": i, "end": i + 1, "text": str(i)} for i in range(3)]
    original = json.loads(json.dumps(chunks))
    vectors = [[0, 1], [1, 0], [0.8, 0.6]]
    hits = rank(chunks, vectors, [1, 0], 2, 0.5)
    assert [h["chunk_id"] for h in hits] == [1, 2] and chunks == original
    assert [h["score"] for h in hits] == [1, 0.8]
    assert all(h["source"] == "原文.txt" and h["start"] == h["chunk_id"] for h in hits)
    assert len(rank(chunks, vectors, [1, 0], 99)) == 3
    assert rank(chunks, vectors, [0, 0]) == []
    assert rank([], [], [1]) == []
    assert rank(chunks, vectors, [-1, 0], 2, 0.5) == []
    for k, score in [(0, 0), (-1, 0), (True, 0), (1, 2), (1, math.nan)]:
        error(lambda: rank(chunks, vectors, [1, 0], k, score))
    error(lambda: rank(chunks, vectors[:1], [1, 0]))
    error(lambda: functions(False)["rank_chunks"](chunks, vectors, [1, 0]), NotImplementedError)
    assert demo("火星氣溫") == [0, 0, 0, 0]
    assert rank(chunks, [[1, 0, 0, 0]] * 3, demo("火星氣溫")) == []
    print("排名：方向／尺度、維度與有限數字、門檻／top_k／空結果、來源保留與原資料不變通過")


class Backend:
    """測試專用HTTP後端；不放入學生教材或正式App。"""
    def __init__(self):
        self.calls = []
        self.settings = []
        self.mode = "good"

    def handler(self, request):
        body = json.loads(request.content)
        self.calls.append(body)
        if self.mode == "timeout":
            raise httpx.ReadTimeout("offline simulated timeout", request=request)
        if self.mode == "429":
            return httpx.Response(429, json={"error": {"message": "offline limit", "type": "rate_limit_error"}})
        demo = functions(True)["demo_vector"]
        data = []
        for i, text in enumerate(body["input"]):
            vector = demo(text)
            if not any(vector):
                vector = [0.2, 0.3, 0.4, 0.5]
            data.append({"object": "embedding", "index": i, "embedding": vector})
        if self.mode == "missing":
            data.pop()
        elif self.mode == "duplicate":
            data[-1]["index"] = 0
        elif self.mode == "dimension":
            data[-1]["embedding"] = [1.0]
        elif self.mode == "zero":
            data[-1]["embedding"] = [0.0] * 4
        elif self.mode == "empty":
            data[-1]["embedding"] = []
        elif self.mode == "bad-number":
            data[-1]["embedding"] = ["NaN", 0.0, 0.0, 1.0]
        elif self.mode == "reversed":
            data.reverse()
        return httpx.Response(200, json={"object": "list", "model": body["model"], "data": data, "usage": {"prompt_tokens": 5, "total_tokens": 5}})

    def client(self, **kwargs):
        self.settings.append({k: kwargs[k] for k in ["max_retries", "timeout"]})
        return REAL_OPENAI(http_client=httpx.Client(transport=httpx.MockTransport(self.handler)), **kwargs)


def check_notebook_api():
    backend = Backend()
    source = "".join(next(c for c in read_book(True)["cells"] if c["id"] == "w10s-real-run")["source"])
    def run(paid=True, key="offline-test-placeholder"):
        backend.calls.clear()
        ns = {"embedding_result": "old"}
        activity = source.replace("RUN_REAL_EMBEDDINGS = False", f"RUN_REAL_EMBEDDINGS = {paid}")
        with patch.object(openai, "OpenAI", backend.client), patch("dotenv.load_dotenv"), patch.dict(os.environ, {"OPENAI_API_KEY": key}), redirect_stdout(StringIO()):
            exec(activity, ns)
        return ns
    assert run(False)["embedding_result"] is None and not backend.calls
    for mode in ["good", "reversed"]:
        backend.mode = mode
        result = run()
        assert result["embedding_result"] and not result["embedding_error"] and len(backend.calls) == 1
        assert len(backend.calls[0]["input"]) == 6 and backend.calls[0]["encoding_format"] == "float"
        assert "store" not in backend.calls[0]
    backend.mode = "good"
    assert run(key="")["embedding_error"] and not backend.calls
    for mode in ["missing", "duplicate", "dimension", "zero", "empty", "bad-number", "429", "timeout"]:
        backend.mode = mode
        result = run()
        assert result["embedding_result"] is None and result["embedding_error"] and len(backend.calls) == 1, mode
    assert all(s == {"max_retries": 0, "timeout": 60.0} for s in backend.settings)
    print("Notebook API：真實SDK＋MockTransport驗證0／1次、合批6筆、index對齊、回應檢查、缺key、429／逾時無重試與清舊資料通過")


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
    with patch.object(openai, "OpenAI", backend.client), patch.object(st, "secrets", {}), patch.object(st, "download_button", download), patch("dotenv.load_dotenv"), patch.dict(os.environ, {"OPENAI_API_KEY": "offline-test-placeholder"}):
        teacher = AppTest.from_file(str(PACKAGE / "teacher/app.py"), default_timeout=20).run()
        assert not teacher.exception and not backend.calls
        submit(teacher)
        assert downloads and downloads[-1]["mode"] == "離線規則示範" and not backend.calls
        record = teacher.session_state["record"]
        for item in record["chunks"]:
            assert item["text"] == record["source"][item["start"]:item["end"]]
        teacher.slider[0].set_value(1).run()
        assert not backend.calls and downloads[-1]["top_k"] == 1
        teacher.text_input[0].set_value("火星氣溫")
        submit(teacher)
        assert downloads[-1]["hits"] == []
        teacher.checkbox[0].check().run()
        assert teacher.session_state["record"] is None and not backend.calls
        teacher.text_input[0].set_value("工作坊地點在哪裡？")
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            submit(teacher)
            assert teacher.error and not backend.calls and not downloads
        submit(teacher)
        assert len(backend.calls) == 1 and downloads[-1]["mode"] == "真實Embeddings API"
        saved = teacher.session_state["record"]
        teacher.slider[0].set_value(2).run()
        teacher.slider[1].set_value(0.5).run()
        teacher.run()
        assert len(backend.calls) == 1 and teacher.session_state["record"] == saved
        assert "vectors" not in downloads[-1] and "api_key" not in downloads[-1]
        for mode in ["missing", "dimension", "zero", "bad-number", "429", "timeout"]:
            backend.mode = "good"
            submit(teacher)
            assert teacher.session_state["record"] is not None
            backend.mode = mode
            before = len(backend.calls)
            submit(teacher)
            assert len(backend.calls) == before + 1
            assert teacher.error and teacher.session_state["record"] is None and not downloads
        backend.mode = "good"
        for value in ["", "A" * 301]:
            before = len(backend.calls)
            teacher.text_input[0].set_value(value)
            submit(teacher)
            assert teacher.error and not downloads and len(backend.calls) == before
        teacher.text_input[0].set_value("工作坊地點在哪裡？")
        for text in [" ", "A" * 6001, "A" * 1001, "\n\n".join(["一段"] * 13)]:
            before = len(backend.calls)
            teacher.text_area[0].set_value(text)
            submit(teacher)
            assert teacher.error and not downloads and len(backend.calls) == before
        teacher.text_area[0].set_value("  地點是圖書館。\r\n\r\n  報名未公告。 ")
        submit(teacher)
        for item in teacher.session_state["record"]["chunks"]:
            assert item["text"] == teacher.session_state["record"]["source"][item["start"]:item["end"]]
        teacher.button[0].click().run()
        assert teacher.session_state["record"] is None
        student = AppTest.from_file(str(PACKAGE / "student/app.py"), default_timeout=20).run()
        student.checkbox[0].check().run()
        before = len(backend.calls)
        submit(student)
        assert student.error and len(backend.calls) == before and not downloads
        # 只移入A即可成功；保留其他程式與檔案位置。
        student_source = (PACKAGE / "student/app.py").read_text(encoding="utf-8")
        teacher_source = (PACKAGE / "teacher/app.py").read_text(encoding="utf-8")
        a = next(n for n in ast.parse(student_source).body if isinstance(n, ast.FunctionDef) and n.name == "rank_chunks")
        answer = next(n for n in ast.parse(teacher_source).body if isinstance(n, ast.FunctionDef) and n.name == "rank_chunks")
        lines = student_source.splitlines(keepends=True)
        completed = "".join(lines[:a.lineno - 1]) + ast.get_source_segment(teacher_source, answer) + "\n" + "".join(lines[a.end_lineno:])
        path = PACKAGE / "student/.verify_completed.py"
        try:
            path.write_text(completed, encoding="utf-8")
            at = AppTest.from_file(str(path), default_timeout=20).run()
            submit(at)
            assert downloads and not at.error
        finally:
            path.unlink(missing_ok=True)
    print("AppTest：雙版0請求啟動、A阻擋與移入成功、離線／模擬真實、滑桿與rerun不重送、來源位置、超限與API失敗清舊結果通過")


def check_rebuild_and_preservation():
    files = list(WEEK.glob("*課堂簡化版_*.ipynb")) + list(WEEK.glob("*課堂簡化版_*.md")) + [p for p in PACKAGE.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    before = {p: p.read_bytes() for p in files}
    subprocess.run([sys.executable, "-B", "-X", "utf8", str(ROOT / "scripts/build_week10_simple.py")], check=True, capture_output=True)
    assert all(p.read_bytes() == content for p, content in before.items())
    for path in list(WEEK.glob("*課堂簡化版*.md")) + [PACKAGE / "README.md"]:
        text = path.read_text(encoding="utf-8")
        assert "\ufffd" not in text and "???" not in text
        assert len(re.findall(r"^```", text, re.M)) % 2 == 0
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if not target.startswith(("https://", "http://", "#")):
                assert (path.parent / target.split("#")[0]).exists(), (path, target)
    snapshot = TEMP / "before.json"
    if snapshot.exists():
        saved = json.loads(snapshot.read_text(encoding="utf-8"))
        for name, checksum in saved["hashes"].items():
            if name == "PROJECT_MEMORY.md":
                continue
            assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == checksum, name
    print("重建一致、相對連結與原有已追蹤檔案雜湊保留通過")


def main():
    check_notebooks()
    check_ranking()
    check_notebook_api()
    check_apps()
    check_rebuild_and_preservation()
    print("全部離線驗證通過；0次真實API，未測真實搜尋品質、真人瀏覽器、Colab、Cloud或試教。")


if __name__ == "__main__":
    main()
