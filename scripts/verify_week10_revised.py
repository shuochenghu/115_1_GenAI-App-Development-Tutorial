"""第10週修訂版離線驗證；真實SDK＋MockTransport，不送出網路請求。"""
import ast
from contextlib import redirect_stdout
from io import StringIO
import json
import math
import os
from pathlib import Path
import re
import runpy
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
PACKAGE = WEEK / "week10_semantic_search_revised"
PREFIX = "w10r-"
TEMP = ROOT / "output/week10_revised_checks"
TEMP.mkdir(parents=True, exist_ok=True)
(TEMP / ".gitignore").write_text("*\n", encoding="utf-8")
tempfile.tempdir = str(TEMP.resolve())
REAL_OPENAI = openai.OpenAI
BUILD = runpy.run_path(str(ROOT / "scripts/build_week10_revised.py"))
for name in [k for k in os.environ if k.startswith("OPENAI_")]:
    del os.environ[name]


def read_book(teacher):
    ending = "教師版" if teacher else "學生版"
    return json.loads(next(WEEK.glob(f"*課堂簡化版_修訂版_{ending}.ipynb")).read_text(encoding="utf-8"))


def functions(teacher, path=None):
    path = path or PACKAGE / ("teacher" if teacher else "student") / "app.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    nodes = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))]
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


def error(call, kind=ValueError):
    try:
        call()
    except kind:
        return
    raise AssertionError("未拒絕錯誤輸入")


def check_data_continuity():
    """本週資料必須等於第9週修訂版clean_text處理sample.txt的結果。"""
    week9 = functions(True, ROOT / "week09/week09_document_revised/teacher/app.py")
    raw = week9["extract_text"]("sample.txt", (ROOT / "week09/sample_tata/sample.txt").read_bytes())
    cleaned = week9["clean_text"](raw)
    assert cleaned == BUILD["DOC"]
    assert (PACKAGE / "sample_data/week09_cleaned_text.txt").read_text(encoding="utf-8").strip() == cleaned
    questions = json.loads((PACKAGE / "sample_data/questions.json").read_text(encoding="utf-8"))
    assert [q["query"] for q in questions] == [q["query"] for q in BUILD["QUESTIONS"]]
    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
    for q in questions:
        if q["expected_chunk_id"] is not None:
            assert q["evidence"] in paragraphs[q["expected_chunk_id"]], q
    print("資料：與第9週修訂版clean_text(sample.txt)完全相同、問題清單與證據位置一致通過")


def check_notebooks():
    books = [read_book(False), read_book(True)]
    assert [c["id"] for c in books[0]["cells"]] == [c["id"] for c in books[1]["cells"]]
    for s, t in zip(books[0]["cells"], books[1]["cells"]):
        if s["id"] not in [PREFIX + "cover", PREFIX + "a", PREFIX + "b-reference"]:
            assert s == t, s["id"]
    for teacher, book in zip([False, True], books):
        cells = book["cells"]
        assert len(cells) == 32 and len(cells) == len({c["id"] for c in cells})
        by_id = {c["id"].removeprefix(PREFIX): c for c in cells}
        namespace = {}
        with tempfile.TemporaryDirectory(dir=TEMP) as folder:
            old = Path.cwd()
            os.chdir(folder)
            try:
                for cell in cells:
                    text = "".join(cell["source"])
                    assert "�" not in text and "???" not in text
                    if cell["cell_type"] == "markdown":
                        headings = re.findall(r"^#{1,6} .+", re.sub(r"```.*?```", "", text, flags=re.S), re.M)
                        assert not headings or (len(headings) == 1 and text.startswith("#")), cell["id"]
                        continue
                    assert cell["outputs"] == [] and cell["execution_count"] is None
                    first_line = text.splitlines()[0]
                    assert first_line.startswith("# 用途：") and "先備：" in first_line, cell["id"]
                    ast.parse(text)
                    with redirect_stdout(StringIO()):
                        exec(text, namespace)
                    fresh = {}
                    for dependency in cell["metadata"]["teaching"]["requires"]:
                        with redirect_stdout(StringIO()):
                            exec("".join(by_id[dependency]["source"]), fresh)
                    with redirect_stdout(StringIO()):
                        exec(text, fresh)
            finally:
                os.chdir(old)
        assert namespace["embedding_result"] is None and namespace["embedding_error"] is None
        assert namespace["teacher_record"] is None and namespace["real_rankings"] is None
        assert (namespace["hits_result"] is not None) == teacher
        assert namespace["document"] == BUILD["DOC"] and len(namespace["chunks"]) == 3
        if teacher:
            found = [[h["chunk_id"] for h in r["hits"]] for r in namespace["offline_results"]]
            assert found == [[0], [], [2], []]   # 改寫題離線找不到，正是教學對照
        else:
            assert namespace["offline_results"] is None
        assert ("raise NotImplementedError" in "".join(by_id["a"]["source"])) != teacher
        ending = "教師版" if teacher else "學生版"
        reading = next(WEEK.glob(f"*課堂簡化版_修訂版_{ending}.md")).read_text(encoding="utf-8")
        for cell in cells:
            assert "".join(cell["source"]) in reading
        app_tree = ast.parse((PACKAGE / ("teacher" if teacher else "student") / "app.py").read_text(encoding="utf-8"))
        for tag, name in [("a", "rank_chunks"), ("cosine-fn", "cosine_similarity"), ("demo-fn", "demo_vector")]:
            node = next(n for n in ast.parse("".join(by_id[tag]["source"])).body if isinstance(n, ast.FunctionDef))
            actual = next(n for n in app_tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
            assert ast.dump(node) == ast.dump(actual), name
        for cell in cells:
            assert "原教材保留" not in "".join(cell["source"])
    print(f"Notebook：雙版各{len(books[0]['cells'])}格，JSON／ID／輸出／可見用途與先備／AST／先備獨立與順序／答案分離／離線對照結果／Markdown與App對齊通過")


def check_ranking():
    ns = functions(True)
    cosine, rank, demo = [ns[name] for name in ["cosine_similarity", "rank_chunks", "demo_vector"]]
    assert cosine([1, 0], [5, 0]) == 1 and cosine([1, 0], [-1, 0]) == -1
    assert cosine([1, 0], [0, 1]) == 0 and cosine([0, 0], [1, 0]) == 0
    for a, b in [([], []), ([1], [1, 2]), ([math.nan], [1]), ([math.inf], [1]), ([True], [1])]:
        error(lambda: cosine(a, b))
    chunks = [{"chunk_id": i, "source": "原文.txt", "start": i, "end": i + 1, "text": str(i)} for i in range(3)]
    original = json.loads(json.dumps(chunks))
    vectors = [[0, 1], [1, 0], [0.8, 0.6]]
    hits = rank(chunks, vectors, [1, 0], 2, 0.5)
    assert [h["chunk_id"] for h in hits] == [1, 2] and chunks == original
    assert [h["score"] for h in hits] == [1, 0.8]
    assert len(rank(chunks, vectors, [1, 0], 99)) == 3
    assert rank(chunks, vectors, [0, 0]) == [] and rank([], [], [1]) == []
    assert rank(chunks, vectors, [-1, 0], 2, 0.5) == []
    for k, score in [(0, 0), (-1, 0), (True, 0), (1, 2), (1, math.nan)]:
        error(lambda: rank(chunks, vectors, [1, 0], k, score))
    error(lambda: rank(chunks, vectors[:1], [1, 0]))
    error(lambda: functions(False)["rank_chunks"](chunks, vectors, [1, 0]), NotImplementedError)
    assert demo("火星氣溫") == [0, 0, 0, 0] and demo("這場讀書交流辦在哪個空間？") == [0, 0, 0, 0]
    print("排名：方向／尺度、維度與有限數字、門檻／top_k／空結果、來源保留、原資料不變、改寫題規則全零通過")


class Backend:
    """測試專用HTTP後端；不放入學生教材或正式App。"""
    def __init__(self):
        self.calls, self.settings, self.mode = [], [], "good"

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
        return httpx.Response(200, json={"object": "list", "model": body["model"], "data": data,
                                         "usage": {"prompt_tokens": 5, "total_tokens": 5}})

    def client(self, **kwargs):
        self.settings.append({k: kwargs[k] for k in ["max_retries", "timeout"]})
        return REAL_OPENAI(http_client=httpx.Client(transport=httpx.MockTransport(self.handler)), **kwargs)


def check_notebook_api():
    backend = Backend()
    code = {c["id"].removeprefix(PREFIX): "".join(c["source"]) for c in read_book(True)["cells"] if c["cell_type"] == "code"}

    def run(paid=True, key="offline-test-placeholder"):
        backend.calls.clear()
        ns = {"embedding_result": "old"}
        with patch.object(openai, "OpenAI", backend.client), patch("dotenv.load_dotenv"), \
                patch.dict(os.environ, {"OPENAI_API_KEY": key}), redirect_stdout(StringIO()):
            for tag in ("data", "cosine-fn", "a"):
                exec(code[tag], ns)
            exec(code["real-run"].replace("RUN_REAL_EMBEDDINGS = False", f"RUN_REAL_EMBEDDINGS = {paid}"), ns)
        return ns

    assert run(False)["embedding_result"] is None and not backend.calls
    for mode in ["good", "reversed"]:
        backend.mode = mode
        result = run()
        assert result["embedding_result"] and not result["embedding_error"] and len(backend.calls) == 1
        assert len(backend.calls[0]["input"]) == 7 and backend.calls[0]["encoding_format"] == "float"
        assert backend.calls[0]["input"][:3] == [c["text"] for c in result["chunks"]]
        assert "store" not in backend.calls[0]
    backend.mode = "good"
    assert run(key="")["embedding_error"] and not backend.calls
    for mode in ["missing", "duplicate", "dimension", "zero", "empty", "bad-number", "429", "timeout"]:
        backend.mode = mode
        result = run()
        assert result["embedding_result"] is None and result["embedding_error"] and len(backend.calls) == 1, mode
    assert all(s == {"max_retries": 0, "timeout": 60.0} for s in backend.settings)

    # 真實排名→教師紀錄存檔→7-2讀回；紀錄不含向量
    backend.mode = "good"
    ns = run()
    with tempfile.TemporaryDirectory(dir=TEMP) as folder:
        old = Path.cwd()
        os.chdir(folder)
        try:
            with redirect_stdout(StringIO()):
                exec(code["real-rank"].replace("SAVE_TEACHER_RECORD = False", "SAVE_TEACHER_RECORD = True"), ns)
                assert len(ns["real_rankings"]) == 4 and Path("teacher_ranking_record.json").exists()
                saved = json.loads(Path("teacher_ranking_record.json").read_text(encoding="utf-8"))
                assert "vectors" not in json.dumps(saved) and saved["note"].startswith("教師課前實測")
                fresh = {}
                exec(code["teacher-record-run"], fresh)
                assert fresh["teacher_record"]["rankings"] == ns["real_rankings"]
        finally:
            os.chdir(old)
    print("Notebook API：真實SDK＋MockTransport驗證0／1次、合批7筆、index對齊、回應檢查、缺key、429／逾時無重試、教師紀錄存讀與不含向量通過")


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

    with patch.object(openai, "OpenAI", backend.client), patch.object(st, "secrets", {}), \
            patch.object(st, "download_button", download), patch("dotenv.load_dotenv"), \
            patch.dict(os.environ, {"OPENAI_API_KEY": "offline-test-placeholder"}):
        teacher = AppTest.from_file(str(PACKAGE / "teacher/app.py"), default_timeout=20).run()
        assert not teacher.exception and not backend.calls
        assert teacher.text_area[0].value.strip() == BUILD["DOC"]
        submit(teacher)
        assert downloads and downloads[-1]["mode"] == "離線規則示範" and not backend.calls
        assert [h["chunk_id"] for h in downloads[-1]["hits"]][:1] == [0]
        record = teacher.session_state["record"]
        assert len(record["chunks"]) == 3
        for item in record["chunks"]:
            assert item["text"] == record["source"][item["start"]:item["end"]]
        teacher.slider[0].set_value(1).run()
        assert not backend.calls and downloads[-1]["top_k"] == 1
        teacher.text_input[0].set_value("這場讀書交流辦在哪個空間？")
        submit(teacher)
        assert downloads[-1]["hits"] == []   # 離線規則找不到改寫題
        teacher.checkbox[0].check().run()
        assert teacher.session_state["record"] is None and not backend.calls
        teacher.text_input[0].set_value("活動地點在哪裡？")
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
        teacher.text_input[0].set_value("活動地點在哪裡？")
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
        student_source = (PACKAGE / "student/app.py").read_text(encoding="utf-8")
        assert BUILD["RANK_STUDENT"] in student_source
        path = PACKAGE / "student/.verify_completed.py"
        try:
            path.write_text(student_source.replace(BUILD["RANK_STUDENT"], BUILD["RANK_TEACHER"]), encoding="utf-8")
            at = AppTest.from_file(str(path), default_timeout=20).run()
            submit(at)
            assert downloads and not at.error
        finally:
            path.unlink(missing_ok=True)
    print("AppTest：雙版0請求啟動、預設文字＝第9週清理後文字、A阻擋與移入成功、離線改寫題找不到、模擬真實、滑桿與rerun不重送、來源位置、超限與API失敗清舊結果通過")


def check_settings():
    """金鑰在本機（.env／環境變數）、Streamlit Cloud（Secrets）與Notebook都讀得到；入口同層有requirements。"""
    from streamlit.errors import StreamlitSecretNotFoundError

    class NoSecretsFile:   # 本機沒有secrets.toml時，Streamlit的實際行為
        def get(self, *args):
            raise StreamlitSecretNotFoundError("no secrets.toml")

    for teacher in (False, True):
        read = functions(teacher)["read_setting"]
        with patch.dict(os.environ, {"OPENAI_API_KEY": "from-env"}):
            with patch.object(st, "secrets", NoSecretsFile()):
                assert read("OPENAI_API_KEY") == "from-env"
            with patch.object(st, "secrets", {}):
                assert read("OPENAI_API_KEY") == "from-env"
            with patch.object(st, "secrets", {"OPENAI_API_KEY": "from-cloud"}):
                assert read("OPENAI_API_KEY") == "from-cloud"
        with patch.object(st, "secrets", NoSecretsFile()):
            assert read("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small") == "text-embedding-3-small"
        source = (PACKAGE / ("teacher" if teacher else "student") / "app.py").read_text(encoding="utf-8")
        assert "load_dotenv(Path(__file__).resolve().parents[1] / '.env')" in source
    # 實際從.env讀到金鑰：入口資料夾一份可用；App資料夾也有時以App資料夾優先
    with tempfile.TemporaryDirectory(dir=TEMP) as folder:
        target = Path(folder)
        for name in ["teacher/app.py", "sample_data/week09_cleaned_text.txt"]:
            (target / name).parent.mkdir(parents=True, exist_ok=True)
            (target / name).write_bytes((PACKAGE / name).read_bytes())
        for files, expected in [({"teacher/.env": "from-entry-env"}, "from-entry-env"),
                                ({".env": "from-app-folder-env"}, "from-app-folder-env")]:
            for name, value in files.items():
                (target / name).write_text(f"OPENAI_API_KEY={value}\n", encoding="utf-8")
            os.environ.pop("OPENAI_API_KEY", None)
            try:
                with patch.object(st, "secrets", {}):
                    AppTest.from_file(str(target / "teacher/app.py"), default_timeout=20).run()
                    assert os.environ.get("OPENAI_API_KEY") == expected
            finally:
                os.environ.pop("OPENAI_API_KEY", None)
    deps = lambda path: [l for l in path.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    for folder in ("student", "teacher"):
        assert deps(PACKAGE / folder / "requirements.txt") == deps(PACKAGE / "requirements.txt")
    real_run = "".join(next(c for c in read_book(False)["cells"] if c["id"] == PREFIX + "real-run")["source"])
    assert 'load_dotenv("week10_semantic_search_revised/.env")' in real_run
    print("金鑰設定：Secrets優先、無secrets.toml時讀環境變數／.env、Notebook讀App資料夾.env、入口同層requirements通過")


def check_rebuild_and_links():
    files = [*WEEK.glob("*修訂版_*.ipynb"), *WEEK.glob("*修訂版_*.md"),
             *(p for p in PACKAGE.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.name != "README.md")]
    before = {p: p.read_bytes() for p in files}
    subprocess.run([sys.executable, "-B", "-X", "utf8", str(ROOT / "scripts/build_week10_revised.py")], check=True, capture_output=True)
    assert all(p.read_bytes() == content for p, content in before.items())
    for path in [*WEEK.glob("*修訂版*.md"), PACKAGE / "README.md"]:
        text = path.read_text(encoding="utf-8")
        assert "�" not in text and "???" not in text
        assert len(re.findall(r"^```", text, re.M)) % 2 == 0
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if not target.startswith(("https://", "http://", "#")):
                assert (path.parent / target.split("#")[0]).exists(), (path, target)
    print("重建一致、UTF-8、Markdown與本機連結通過")


def main():
    check_data_continuity()
    check_notebooks()
    check_ranking()
    check_notebook_api()
    check_apps()
    check_settings()
    check_rebuild_and_links()
    import importlib.metadata as md
    print("Runtime:", sys.version.split()[0], {n: md.version(n) for n in ("streamlit", "openai", "python-dotenv", "httpx")})
    print("全部離線驗證通過；0次真實API，未測真實搜尋品質、真人瀏覽器、Colab、Cloud或試教。")


if __name__ == "__main__":
    main()
