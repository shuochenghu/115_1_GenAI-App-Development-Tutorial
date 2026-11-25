"""第11週修訂版（重新規劃後：只教自行建置RAG）離線驗證；真實SDK＋MockTransport，不送出網路請求。"""
import ast
from contextlib import redirect_stdout
from io import BytesIO, StringIO
import json
import os
from pathlib import Path
import re
import runpy
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
PACKAGE = WEEK / "week11_rag_revised"
PREFIX = "w11r-"
TEMP = ROOT / "output/week11_revised_checks"
TEMP.mkdir(parents=True, exist_ok=True)
(TEMP / ".gitignore").write_text("*\n", encoding="utf-8")
tempfile.tempdir = str(TEMP.resolve())
REAL_OPENAI = openai.OpenAI
BUILD = runpy.run_path(str(ROOT / "scripts/build_week11_revised.py"))
LACK = "根據目前文件，無法確認這個問題。"
for name in [k for k in os.environ if k.startswith("OPENAI_")]:
    del os.environ[name]

# Notebook與App要一模一樣的函式與常數
APP_FUNCTIONS = {
    "data": ["split_chunks"], "week10-fns": ["demo_vector", "cosine_similarity", "rank_chunks"],
    "a": ["build_context"], "policy": ["build_input"], "check-fns": ["check_answer"],
    "rag-fns": ["embed_texts", "answer_question"],
}
APP_CONSTANTS = {"policy": ["INSUFFICIENT", "INSTRUCTIONS"]}


def read_book(teacher):
    ending = "教師版" if teacher else "學生版"
    return json.loads(next(WEEK.glob(f"*RAG文件問答_課堂簡化版_修訂版_{ending}.ipynb")).read_text(encoding="utf-8"))


def functions(teacher=True, path=None):
    path = path or PACKAGE / ("teacher" if teacher else "student") / "app.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    nodes = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))
             or (isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id.isupper())]
    namespace = {"__file__": str(path)}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


def run_quiet(source, namespace):
    output = StringIO()
    with redirect_stdout(output):
        exec(source, namespace)
    return output.getvalue()


def check_data_continuity():
    """資料與問題必須等於第10週修訂版（也就是第9週修訂版clean_text處理sample.txt的結果）。"""
    week10 = ROOT / "week10/week10_semantic_search_revised/sample_data"
    assert (PACKAGE / "sample_data/week09_cleaned_text.txt").read_bytes() == (week10 / "week09_cleaned_text.txt").read_bytes()
    week9 = functions(True, ROOT / "week09/week09_document_revised/teacher/app.py")
    raw = week9["extract_text"]("sample.txt", (ROOT / "week09/sample_tata/sample.txt").read_bytes())
    assert week9["clean_text"](raw) == BUILD["DOC"]
    mine = json.loads((PACKAGE / "sample_data/questions.json").read_text(encoding="utf-8"))
    theirs = json.loads((week10 / "questions.json").read_text(encoding="utf-8"))
    assert [q["query"] for q in mine] == [q["query"] for q in theirs]
    assert all(q["good_answer"] for q in mine)
    w10 = ast.parse((ROOT / "week10/week10_semantic_search_revised/teacher/app.py").read_text(encoding="utf-8"))
    w11 = ast.parse((PACKAGE / "teacher/app.py").read_text(encoding="utf-8"))
    for name in ["demo_vector", "cosine_similarity", "rank_chunks"]:
        a = next(n for n in w10.body if isinstance(n, ast.FunctionDef) and n.name == name)
        b = next(n for n in w11.body if isinstance(n, ast.FunctionDef) and n.name == name)
        assert ast.dump(a) == ast.dump(b), name
    print("資料：與第10週修訂版同一份文字與4題、等於第9週clean_text(sample.txt)、三個第10週函式AST相同通過")


def check_notebooks():
    books = [read_book(False), read_book(True)]
    assert [c["id"] for c in books[0]["cells"]] == [c["id"] for c in books[1]["cells"]]
    for s, t in zip(books[0]["cells"], books[1]["cells"]):
        if s["id"] not in [PREFIX + "cover", PREFIX + "a", PREFIX + "b-reference"]:
            assert s == t, s["id"]
    for teacher, book in zip([False, True], books):
        cells = book["cells"]
        assert len(cells) == 43 and len(cells) == len({c["id"] for c in cells})
        by_id = {c["id"].removeprefix(PREFIX): c for c in cells}
        namespace, printed = {}, {}
        with tempfile.TemporaryDirectory(dir=TEMP) as folder:
            old = Path.cwd()
            os.chdir(folder)
            try:
                for cell in cells:
                    text = "".join(cell["source"])
                    assert "�" not in text and "???" not in text and "原教材保留" not in text
                    if cell["cell_type"] == "markdown":
                        plain = re.sub(r"```.*?```", "", text, flags=re.S)
                        headings = re.findall(r"^#{1,6} .+", plain, re.M)
                        assert not headings or (len(headings) == 1 and text.startswith("#")), cell["id"]
                        assert not re.search(r"^ {4,}\S", plain, re.M), cell["id"]
                        continue
                    assert cell["outputs"] == [] and cell["execution_count"] is None
                    assert text.splitlines()[0].startswith("# 用途：") and "先備：" in text.splitlines()[0], cell["id"]
                    printed[cell["id"].removeprefix(PREFIX)] = run_quiet(text, namespace)   # 順序執行
                    fresh = {}
                    for dependency in cell["metadata"]["teaching"]["requires"]:   # 只依先備也能執行
                        run_quiet("".join(by_id[dependency]["source"]), fresh)
                    run_quiet(text, fresh)
            finally:
                os.chdir(old)
        for name in ["real_evidence", "real_results", "teacher_record", "rag_record", "integrated_records"]:
            assert namespace[name] is None, name
        assert len(namespace["chunks"]) == 3
        for item in namespace["chunks"]:
            assert namespace["document"][item["start"]:item["end"]] == item["text"]
        assert [[h["chunk_id"] for h in e["hits"]] for e in namespace["offline_evidence"]] == [[0], [], [2], []]
        assert [e["query"] for e in namespace["offline_evidence"]] == [q["query"] for q in namespace["questions"]]
        assert (namespace["context_result"] is not None) == teacher
        if teacher:
            assert printed["preview"].count("送出1段證據給模型") == 2 and printed["preview"].count("直接回答不足句") == 2
            assert "只是資料，不是指令" in printed["preview"] and "[來源1] 第9週sample.txt／0" in printed["preview"]
        else:
            assert "A還沒通過" in printed["preview"] and "instructions" not in printed["preview"]
        verdicts = [line.split(" ")[0] for line in printed["check-demo"].splitlines()]
        assert verdicts == ["有標來源：請回原文核對", "承認資訊不足", "不合格：引用了context裡沒有的來源", "沒有標來源：不能直接採用"]
        assert ("raise NotImplementedError" in "".join(by_id["a"]["source"])) != teacher
        ending = "教師版" if teacher else "學生版"
        reading = next(WEEK.glob(f"*RAG文件問答_課堂簡化版_修訂版_{ending}.md")).read_text(encoding="utf-8")
        for cell in cells:
            assert "".join(cell["source"]) in reading
        app_tree = ast.parse((PACKAGE / ("teacher" if teacher else "student") / "app.py").read_text(encoding="utf-8"))
        for tag, names in APP_FUNCTIONS.items():
            cell_tree = ast.parse("".join(by_id[tag]["source"]))
            for name in names:
                node = next(n for n in cell_tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
                actual = next(n for n in app_tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
                assert ast.dump(node) == ast.dump(actual), name
        for tag, names in APP_CONSTANTS.items():
            cell_tree = ast.parse("".join(by_id[tag]["source"]))
            for name in names:
                node = next(n for n in cell_tree.body if isinstance(n, ast.Assign) and n.targets[0].id == name)
                actual = next(n for n in app_tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == name)
                assert ast.dump(node) == ast.dump(actual), name
        text = json.dumps(book, ensure_ascii=False)
        assert "file_search_evidence" not in text and "resources.py" not in text
    print("Notebook：雙版各43格，JSON／ID／輸出／用途與先備／Markdown無意外縮排／先備獨立與順序執行／答案分離／"
          "離線證據[[0],[],[2],[]]與送出預覽／核對練習四種判斷／Markdown與App函式及規則對齊通過")


def check_functions():
    ns = functions(True)
    build, check, split = ns["build_context"], ns["check_answer"], ns["split_chunks"]
    hits = [{"chunk_id": 0, "source": "a.txt", "text": "第一段"}, {"chunk_id": 2, "source": "a.txt", "text": "第二段"}]
    result = build(hits)
    assert result["text"] == "[來源1] a.txt／0\n第一段\n\n[來源2] a.txt／2\n第二段"
    assert [s["label"] for s in result["sources"]] == ["[來源1]", "[來源2]"] and "label" not in hits[0]
    first = build(hits[:1])
    assert build(hits, len(first["text"])) == first and build(hits, 3) == {"text": "", "sources": []}
    assert build([]) == {"text": "", "sources": []}
    sources = result["sources"]
    assert check("地點[來源1]與日期[來源2]。", sources) == ("有標來源：請回原文核對", ["[來源1]", "[來源2]"])
    assert check("地點【來源1】。", sources)[1] == ["[來源1]"]
    assert check("地點[來源3]。", sources)[0].startswith("不合格")
    assert check(LACK, sources)[0] == "承認資訊不足" and check(LACK.rstrip("。"), [])[0] == "承認資訊不足"
    assert check("地點在圖書館。", sources)[0].startswith("沒有標來源")
    text = "甲段\n\n\n乙段  \n\n丙段"
    for item in split(text, "t"):
        assert text[item["start"]:item["end"]] == item["text"]
    student = functions(False)
    try:
        student["build_context"]([])
        raise AssertionError("學生版A未完成時應該停止")
    except NotImplementedError:
        pass
    print("函式：A標籤／完整原文／空白行／上限不切半／副本、核對四種判斷與全形、分段位置、學生版A未完成會停止通過")


class Backend:
    """測試專用HTTP後端；不放入學生教材或App。"""
    def __init__(self):
        self.calls, self.settings = [], []
        self.mode = "good"

    def handle(self, request):
        path = request.url.path.removeprefix("/v1")
        body = json.loads(request.content) if request.content else None
        self.calls.append((request.method, path, body))
        if self.mode == "timeout":
            raise httpx.ReadTimeout("offline timeout", request=request)
        if self.mode == "429":
            return httpx.Response(429, json={"error": {"message": "offline limit", "type": "rate_limit_error"}})
        if path == "/embeddings":
            demo = functions(True)["demo_vector"]
            data = []
            for i, text in enumerate(body["input"]):
                vector = demo(text)
                data.append({"object": "embedding", "index": i, "embedding": vector + [0.0 if any(vector) else 1.0]})
            return httpx.Response(200, json={"object": "list", "model": body["model"], "data": data,
                                             "usage": {"prompt_tokens": 1, "total_tokens": 1}})
        if path == "/responses":
            question = str(body["input"])
            answer = LACK if ("費用" in question or "火星" in question) else "地點為圖書館討論室[來源1]。"
            content = [{"type": "output_text", "text": answer, "annotations": []}]
            output = [{"id": "msg_test", "type": "message", "role": "assistant", "status": "completed", "content": content}]
            return httpx.Response(200, json={"id": "resp_test", "object": "response", "created_at": 0,
                                             "model": body["model"], "status": "completed", "output": output})
        raise AssertionError((request.method, path))

    def client(self, **kwargs):
        self.settings.append({k: kwargs[k] for k in ["max_retries", "timeout"]})
        return REAL_OPENAI(http_client=httpx.Client(transport=httpx.MockTransport(self.handle)), **kwargs)

    def paths(self):
        return [p for _, p, _ in self.calls]


def check_notebook_api():
    backend = Backend()
    teacher = {c["id"].removeprefix(PREFIX): c for c in read_book(True)["cells"]}
    student_a = "".join(next(c for c in read_book(False)["cells"] if c["id"] == PREFIX + "a")["source"])

    def run(folder, mode="good", paid=True, key="offline-test-placeholder", student=False):
        """依先備執行7-2真實回答格；開關RUN_REAL_RAG在7-1格。"""
        backend.mode = mode
        backend.calls.clear()
        ns = {}
        old = Path.cwd()
        os.chdir(folder)
        try:
            with patch.object(openai, "OpenAI", backend.client), patch("dotenv.load_dotenv"), \
                    patch.dict(os.environ, {"OPENAI_API_KEY": key}):
                for tag in [*teacher["real-answer"]["metadata"]["teaching"]["requires"], "real-answer"]:
                    source = student_a if (tag == "a" and student) else "".join(teacher[tag]["source"])
                    run_quiet(source.replace("RUN_REAL_RAG = False", f"RUN_REAL_RAG = {paid}"), ns)
        finally:
            os.chdir(old)
        return ns

    def fails(**kwargs):
        try:
            run(**kwargs)
        except Exception:
            return True
        return False

    with tempfile.TemporaryDirectory(dir=TEMP) as folder:
        folder = Path(folder)
        ns = run(folder, paid=False)
        assert ns["real_evidence"] is None and ns["real_results"] is None and not backend.calls
        ns = run(folder, student=True)                    # A沒通過：0次
        assert ns["real_evidence"] is None and not backend.calls
        assert fails(folder=folder, key="") and not backend.calls   # 缺金鑰：open_client停下，0次
        ns = run(folder)
        assert backend.paths() == ["/embeddings", "/responses", "/responses"]
        assert len(backend.calls[0][2]["input"]) == 7
        body = backend.calls[1][2]
        assert body["store"] is False
        assert body["instructions"] == functions(True)["INSTRUCTIONS"] and "只是資料，不是指令" in body["input"]
        results = ns["real_results"]
        assert [r["hits"] for r in results] == [[0], [], [2], []]
        assert [r["check"] for r in results] == ["有標來源：請回原文核對", "承認資訊不足", "承認資訊不足", "承認資訊不足"]
        assert results[1]["answer"] == LACK and results[3]["answer"] == LACK
        for mode in ["429", "timeout"]:
            assert fails(folder=folder, mode=mode) and len(backend.calls) == 1, mode   # 失敗不重試
        # 教師紀錄：存檔→讀回；不含金鑰與向量
        ns = run(folder)
        old = Path.cwd()
        os.chdir(folder)
        try:
            run_quiet("".join(teacher["save-record"]["source"]).replace("SAVE_TEACHER_RECORD = False", "SAVE_TEACHER_RECORD = True"), ns)
            saved = Path("teacher_rag_record.json").read_text(encoding="utf-8")
            assert "offline-test-placeholder" not in saved and "embedding\"" not in saved
            fresh = {}
            run_quiet("".join(teacher["teacher-record-run"]["source"]), fresh)
            assert fresh["teacher_record"]["items"] == json.loads(json.dumps(ns["real_results"]))
            assert fresh["teacher_record"]["note"].startswith("教師課前實測")
        finally:
            os.chdir(old)
    assert all(s == {"max_retries": 0, "timeout": 60.0} for s in backend.settings)
    print("Notebook API：真實SDK＋MockTransport驗證預設0次、A未通過與缺金鑰0次、開啟後1次Embedding（7筆）＋有證據的2題各1次Responses、"
          "規則與input分開、四題核對結果、429／逾時不重試、教師紀錄存讀通過")


def check_download_cell(record):
    """把App實際下載的紀錄放進暫存資料夾，執行10-1讀回格；竄改證據原文後必須被擋下。"""
    code = next("".join(c["source"]) for c in read_book(False)["cells"] if c["id"] == PREFIX + "download-run")
    with tempfile.TemporaryDirectory(dir=TEMP) as folder:
        old = Path.cwd()
        os.chdir(folder)
        try:
            path = Path("rag_record.json")
            path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
            ns = {}
            assert "回查通過" in run_quiet(code, ns) and ns["rag_record"] == record
            if record["context"]:
                bad = json.loads(json.dumps(record))
                bad["hits"][0]["text"] += "（被改過）"
                path.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
                try:
                    run_quiet(code, {})
                except AssertionError:
                    pass
                else:
                    raise AssertionError("竄改證據的紀錄沒有被擋下")
        finally:
            os.chdir(old)


def check_integrated_cell():
    """用AppTest實際操作整合App、收集下載的紀錄，再執行10-2檢查格：用真實API（MockTransport）做完四類問題、
    參數比較、自己的文件與兩則觀察才通過；只有離線紀錄、缺項、範例改名上傳、手改或冒充真實API的紀錄都要被擋下。"""
    app = WEEK / "week11_rag_integrated_revised/app.py"
    code = "".join(next(c for c in read_book(False)["cells"] if c["id"] == PREFIX + "integrated-run")["source"])
    filled = code.replace('": "待填"', '": "改成門檻0.5後只剩chunk 0，費用那段被擋在門檻外"', 1)
    filled = filled.replace('": "待填"', '": "工具那題問題向量全零，屬於檢索找不到，不是生成答錯"', 1)
    backend, downloads, names = Backend(), [], set()
    own_text = "社區清潔日在河濱公園舉行，集合地點是北側入口。\n\n報名截止日期是12月5日，名額40人。".encode("utf-8")
    renamed_bytes = (WEEK / "week11_rag_integrated_revised/sample_data/sample.txt").read_bytes()

    class Upload(BytesIO):
        def __init__(self, name, data):
            super().__init__(data)
            self.name = name

    def download(label, data, file_name=None, **kwargs):
        names.add(file_name)
        if file_name == "integrated_rag_record.json":
            downloads.append(json.loads(data))
        return False

    def click(at, key):
        at.button(key=key).click().run()
        assert not at.exception, at.exception

    def collect(real_api):
        """照講義操作一次：範例四題、同題改門檻、上傳自己的文件2題、範例改名上傳2題；真實模式每題都按回答。"""
        def ask(at, question):
            at.text_input(key="question").set_value(question).run()
            click(at, "retrieve")
            if real_api:
                click(at, "answer")
            return downloads[-1]

        def prepare(at):
            click(at, "prepare")
            click(at, "embed_document")

        at = AppTest.from_file(str(app), default_timeout=30).run()
        if real_api:
            at.checkbox(key="real_api").check().run()
        prepare(at)
        sample = [ask(at, BUILD["QUESTIONS"][0]["query"])]
        at.slider(key="min_score").set_value(0.5).run()
        compared = ask(at, BUILD["QUESTIONS"][0]["query"])        # 同一題只改門檻：沿用問題向量，0次Embedding
        sample += [ask(at, q["query"]) for q in BUILD["QUESTIONS"][1:]]
        at.radio(key="source").set_value("上傳檔案").run()
        with patch.object(st, "file_uploader", return_value=Upload("我的公告.md", own_text)):
            at.run()
            prepare(at)
            own = [ask(at, "集合地點在哪裡？"), ask(at, "需要帶什麼工具？")]
        with patch.object(st, "file_uploader", return_value=Upload("我的文件.txt", renamed_bytes)):
            at.run()
            prepare(at)
            renamed = [ask(at, "活動地點在哪裡？"), ask(at, "報名截止是哪天？")]
        return sample, compared, own, renamed

    with patch.object(openai, "OpenAI", backend.client), patch("dotenv.load_dotenv"),             patch.object(st, "secrets", {}), patch.object(st, "download_button", download),             patch.dict(os.environ, {"OPENAI_API_KEY": "offline-test-placeholder"}):
        offline = collect(False)
        assert not backend.calls
        sample, compared, own, renamed = collect(True)
    paths = [p for _, p, _ in backend.calls]
    # 3份文件各1次＋8個問題各1次Embedding（改門檻重排沿用問題向量）；有證據才回答：範例2題＋改門檻1題＋自己的文件1題＋改名範例2題
    assert paths.count("/embeddings") == 11 and paths.count("/responses") == 6, paths
    assert all(r["mode"] == "真實API" and r["answer"] for r in [*sample, compared, *own, *renamed])
    assert "offline-test-placeholder" not in json.dumps([*sample, compared, *own])
    assert "rag_record.json" not in names   # 整合App不再用第11週App的檔名，Colab裡不會互相覆蓋

    week11_app_record = {"mode": "離線", "question": "活動地點在哪裡？", "hits": [], "context": "", "answer": None, "check": "x"}
    good = [*sample, compared, *own]
    offline_good = [*offline[0], offline[1], *offline[2]]

    def run(records, source=filled):
        """把紀錄依瀏覽器的命名方式存檔（同資料夾另放兩份第11週App紀錄），再執行檢查格；
        回傳印出的文字或AssertionError訊息。"""
        with tempfile.TemporaryDirectory(dir=TEMP) as folder:
            old = Path.cwd()
            os.chdir(folder)
            try:
                for name in ("rag_record.json", "rag_record (1).json"):   # 第11週App的作業紀錄，10-2不讀
                    Path(name).write_text(json.dumps(week11_app_record, ensure_ascii=False), encoding="utf-8")
                for i, record in enumerate(records):
                    name = "integrated_rag_record.json" if i == 0 else f"integrated_rag_record ({i}).json"
                    Path(name).write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
                ns = {}
                try:
                    return run_quiet(source, ns), ns
                except AssertionError as exc:
                    return "AssertionError:" + str(exc), ns
            finally:
                os.chdir(old)

    printed, ns = run([*offline_good, *good])     # 離線練習的紀錄可以留著
    assert "整合App執行檢查通過" in printed and len(ns["integrated_records"]) == len(offline_good) + len(good), printed
    assert f"真實API {len(good)}份，離線{len(offline_good)}份" in printed, printed
    printed, ns = run([])
    assert "尚未找到整合App的紀錄" in printed and ns["integrated_records"] is None
    printed, _ = run([*good, week11_app_record])   # 第11週App紀錄被改成整合App的檔名
    assert printed.startswith("AssertionError:") and "不是整合App下載的紀錄" in printed, printed
    failures = {
        "只有離線紀錄": (offline_good, filled),
        "觀察沒寫": (good, code),
        "少一類問題": ([*sample[:3], compared, *own], filled),
        "少的那題只有離線": ([*sample[:3], offline[0][3], compared, *own], filled),
        "沒有比較參數": ([*sample, *own], filled),
        "範例改名當自己的文件": ([*sample, compared, *renamed], filled),
        "只問一題自己的文件": ([*sample, compared, own[0]], filled),
    }
    for label, (records, source) in failures.items():
        assert run(records, source)[0].startswith("AssertionError:還有❌"), label

    def tampered(change, base=None):
        bad = json.loads(json.dumps(base or sample[0]))
        change(bad)
        return run([bad, *good[1:]])[0]

    fake_real = lambda r: r.update(mode="真實API", answer="地點為圖書館討論室[來源1]。")   # 離線紀錄只改模式與回答
    edits = {
        "片段原文": lambda r: r["document"]["chunks"][0].update(text=r["document"]["chunks"][0]["text"] + "！"),
        "證據原文": lambda r: r["hits"][0].update(text="地點為體育館。"),
        "排名順序": lambda r: r["ranking"].reverse(),
        "排名少一段": lambda r: r["ranking"].pop(),
        "多塞一段低分證據": lambda r: r["hits"].append(dict(r["ranking"][-1])),
        "context被改": lambda r: r.update(context=r["context"].replace("圖書館", "體育館")),
        "回答被清空": lambda r: r.update(answer=""),
        "引用不存在的來源": lambda r: r.update(used_labels=["[來源9]"]),
        "有證據卻沒呼叫模型": lambda r: r.update(answer_model=None),
    }
    for label, change in edits.items():
        message = tampered(change)
        assert message.startswith("AssertionError:") and "❌" not in message, (label, message)
    message = tampered(fake_real, offline[0][0])
    assert "不是真實API回答後下載的紀錄" in message, message
    print("10-2整合App檢查格：AppTest照講義實際操作整合App兩次（離線、真實API MockTransport：範例四題、改門檻、上傳自己的文件2題），"
          "真實紀錄全部通過且離線紀錄可並存但不計入；請求數11次Embedding＋6次Responses、改門檻重排0次Embedding；同資料夾的第11週App rag_record*.json不讀、"
          "改成整合App檔名會擋下；只有離線紀錄、缺觀察、少一類（或只用離線補）、沒比較參數、範例改名、自己的文件只問1題都擋下；"
          "竄改片段／證據／排名／多塞低分證據／context／回答／引用標籤／回答模型、離線紀錄冒充真實API都擋下；沒有檔案只提示")


def check_apps():
    backend = Backend()
    downloads = []

    def download(label, data, *args, **kwargs):
        downloads.append(json.loads(data))
        return False

    def submit(at):
        downloads.clear()
        at.button[0].click().run()
        assert not at.exception, at.exception

    with tempfile.TemporaryDirectory(dir=TEMP) as folder:
        target = Path(folder)
        for name in ["teacher/app.py", "student/app.py", "sample_data/week09_cleaned_text.txt"]:
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((PACKAGE / name).read_bytes())
        with patch.object(openai, "OpenAI", backend.client), patch.object(st, "secrets", {}), \
                patch.object(st, "download_button", download), patch("dotenv.load_dotenv"), \
                patch.dict(os.environ, {"OPENAI_API_KEY": "offline-test-placeholder"}):
            at = AppTest.from_file(str(target / "teacher/app.py"), default_timeout=20).run()
            assert not at.exception and not backend.calls
            assert at.text_area[0].value.strip() == BUILD["DOC"]
            # 離線：規則找證據、A組context、送出前預覽，0次API
            submit(at)
            record = downloads[-1]
            assert not backend.calls and record["answer"] is None and record["mode"] == "離線"
            assert [h["chunk_id"] for h in record["hits"]] == [0] and "[來源1] 貼入文字／0" in record["context"]
            check_download_cell(record)
            at.text_input[0].set_value("這場讀書交流辦在哪個空間？")
            submit(at)
            assert downloads[-1]["hits"] == [] and downloads[-1]["context"] == "" and not backend.calls
            at.text_input[0].set_value("活動地點在哪裡？")
            # 真實API
            at.checkbox[0].check()
            with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
                submit(at)
                assert at.error and not backend.calls and not downloads and at.session_state["record"] is None
            submit(at)
            assert backend.paths() == ["/embeddings", "/responses"]
            assert downloads[-1]["check"] == "有標來源：請回原文核對" and "[來源1]" in downloads[-1]["answer"]
            assert "offline-test-placeholder" not in json.dumps(downloads[-1])
            check_download_cell(downloads[-1])
            saved = at.session_state["record"]
            at.run()
            assert len(backend.calls) == 2 and at.session_state["record"] == saved   # rerun不重送
            at.text_input[0].set_value("火星的平均氣溫是多少？")
            before = len(backend.calls)
            submit(at)
            assert len(backend.calls) == before + 1 and downloads[-1]["answer"] == LACK   # 只有Embedding
            check_download_cell(downloads[-1])
            at.text_input[0].set_value("活動地點在哪裡？")
            for mode in ["429", "timeout"]:
                backend.mode = mode
                submit(at)
                assert at.error and not downloads and at.session_state["record"] is None, mode
            backend.mode = "good"

            # 學生版：A未完成時0次；只移入A就能完成
            student = AppTest.from_file(str(target / "student/app.py"), default_timeout=20).run()
            submit(student)
            assert student.error and not downloads
            student.checkbox[0].check()
            before = len(backend.calls)
            submit(student)
            assert student.error and len(backend.calls) == before
            source = (target / "student/app.py").read_text(encoding="utf-8")
            assert BUILD["BUILD_STUDENT"] in source
            path = target / "student/completed.py"
            path.write_text(source.replace(BUILD["BUILD_STUDENT"], BUILD["BUILD_TEACHER"]), encoding="utf-8")
            done = AppTest.from_file(str(path), default_timeout=20).run()
            submit(done)
            assert downloads[-1]["hits"][0]["chunk_id"] == 0 and not done.error
    print("AppTest：雙版0請求啟動、預設文字＝第10週資料、離線證據與送出預覽、真實1＋1請求、無證據只送Embedding、"
          "缺金鑰／429／逾時清掉結果、rerun不重送、學生A未完成0請求且只移入A即可、下載紀錄經10-1讀回通過與竄改被擋通過")


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
            with patch.object(st, "secrets", {"OPENAI_API_KEY": "from-cloud"}):
                assert read("OPENAI_API_KEY") == "from-cloud"
        with patch.object(st, "secrets", NoSecretsFile()):
            assert read("OPENAI_MODEL", "gpt-5.4-mini") == "gpt-5.4-mini"
        source = (PACKAGE / ("teacher" if teacher else "student") / "app.py").read_text(encoding="utf-8")
        assert "load_dotenv(PACKAGE / '.env')" in source and "load_dotenv(Path(__file__).resolve().parent / '.env')" in source
    with tempfile.TemporaryDirectory(dir=TEMP) as folder:
        target = Path(folder)
        for name in ["teacher/app.py", "sample_data/week09_cleaned_text.txt"]:
            (target / name).parent.mkdir(parents=True, exist_ok=True)
            (target / name).write_bytes((PACKAGE / name).read_bytes())
        for env_file, expected in [("teacher/.env", "from-entry-env"), (".env", "from-app-folder-env")]:
            (target / env_file).write_text(f"OPENAI_API_KEY={expected}\n", encoding="utf-8")
            try:
                with patch.object(st, "secrets", {}):
                    AppTest.from_file(str(target / "teacher/app.py"), default_timeout=20).run()
                    assert os.environ.get("OPENAI_API_KEY") == expected   # 兩處都有時以App資料夾為準
            finally:
                os.environ.pop("OPENAI_API_KEY", None)
        api_setup = "".join(next(c for c in read_book(False)["cells"] if c["id"] == PREFIX + "api-setup")["source"])
        old = Path.cwd()
        os.chdir(target.parent)
        try:
            (target.parent / "week11_rag_revised").mkdir(exist_ok=True)
            (target.parent / "week11_rag_revised/.env").write_text("OPENAI_API_KEY=from-notebook-env\n", encoding="utf-8")
            ns = {}
            exec(api_setup, ns)
            assert ns["notebook_setting"]("OPENAI_API_KEY") == "from-notebook-env"
        finally:
            os.chdir(old)
            os.environ.pop("OPENAI_API_KEY", None)
            shutil.rmtree(target.parent / "week11_rag_revised", ignore_errors=True)
    deps = lambda path: [l for l in path.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    for folder in ("student", "teacher"):
        assert deps(PACKAGE / folder / "requirements.txt") == deps(PACKAGE / "requirements.txt")
        assert "OPENAI_API_KEY" in (PACKAGE / folder / ".streamlit/secrets.example.toml").read_text(encoding="utf-8")
    assert ".env" in (PACKAGE / ".gitignore").read_text(encoding="utf-8").splitlines()
    print("金鑰設定：Secrets優先、無secrets.toml時讀環境變數、App讀到App資料夾與入口資料夾的.env（前者優先）、"
          "Notebook讀App資料夾.env、入口同層requirements與Secrets範本通過")


def check_rebuild_and_preservation():
    files = [*WEEK.glob("*修訂版_*.ipynb"), *WEEK.glob("*修訂版_*.md"),
             *(p for p in PACKAGE.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.name != "README.md")]
    before = {p: p.read_bytes() for p in files}
    subprocess.run([sys.executable, "-B", "-X", "utf8", str(ROOT / "scripts/build_week11_revised.py")], check=True, capture_output=True)
    assert all(p.read_bytes() == content for p, content in before.items())
    assert not (PACKAGE / "resources.py").exists()
    for path in [*WEEK.glob("*修訂版*.md"), PACKAGE / "README.md"]:
        text = path.read_text(encoding="utf-8")
        assert "�" not in text and "???" not in text
        assert len(re.findall(r"^```", text, re.M)) % 2 == 0
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if not target.startswith(("https://", "http://", "#")):
                assert (path.parent / target.split("#")[0]).exists(), (path, target)
    status = subprocess.run(["git", "-c", "core.quotepath=false", "status", "--porcelain", "--", "week11"], cwd=ROOT,
                            capture_output=True, text=True, encoding="utf-8", check=True).stdout
    # 修訂版可能已提交，重建後會顯示M；只要求原版（非修訂版）檔案沒有被改
    originals = [line for line in status.splitlines() if line.strip() and not line.startswith("??")
                 and "修訂版" not in line and "_revised/" not in line]
    assert not originals, originals
    print("重建一致、不再產生resources.py、UTF-8、Markdown圍欄與本機連結、原第11週檔案無修改通過")


def check_dependency_notes():
    """每個用到前面格子變數／函式的程式格，都在格首寫出名稱、短說明與出處；出處（含間接）都在requires。"""
    from notebook_cell_notes import check_dependency_notes as check
    total = 0
    for path in sorted(WEEK.glob("*修訂版_*.ipynb")):
        cells = json.loads(path.read_text(encoding="utf-8"))["cells"]
        total += check(cells, PREFIX, BUILD["CELL_NOUNS"], BUILD["TAG_ALIASES"], BUILD["DIRECT_PREREQ"])
    print(f"格首標註：雙版共{total}個程式格，用到的前面名稱都有短說明與出處，出處（含間接）都在requires，先備寫出直接需要的格子通過")


def main():
    check_dependency_notes()
    check_data_continuity()
    check_notebooks()
    check_functions()
    check_notebook_api()
    check_integrated_cell()
    check_apps()
    check_settings()
    check_rebuild_and_preservation()
    import importlib.metadata as md
    print("Runtime:", sys.version.split()[0], {n: md.version(n) for n in ("streamlit", "openai", "python-dotenv", "httpx")})
    print("全部離線驗證通過；0次真實API，未測真實回答品質、真人瀏覽器、Colab、Cloud或試教。")


if __name__ == "__main__":
    main()
