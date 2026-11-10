"""第12週修訂版離線驗證：真實圖片解碼、真實SDK＋MockTransport與AppTest；0次真實API。"""
import ast
import base64
from contextlib import contextmanager, redirect_stdout
import hashlib
from io import BytesIO, StringIO
import json
import math
import os
from pathlib import Path
import random
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

import httpx
import openai
from PIL import Image, ImageOps
import streamlit as st
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
WEEK = ROOT / "week12"
PACKAGE = WEEK / "week12_vision_revised"
PREFIX = "w12r-"
TEMP = ROOT / "output/week12_revised_checks"
TEMP.mkdir(parents=True, exist_ok=True)
(TEMP / ".gitignore").write_text("*\n", encoding="utf-8")
tempfile.tempdir = str(TEMP.resolve())
REAL_OPENAI = openai.OpenAI
BUILD = runpy.run_path(str(ROOT / "scripts/build_week12_revised.py"))
RECEIPT = {"merchant": "DEMO CAFE", "date": "2026-11-11", "total": 300,
           "visible_text": ["Date: 2026-11-11", "TOTAL TWD 300"], "warnings": []}
for name in [k for k in os.environ if k.startswith("OPENAI_")]:
    del os.environ[name]


@contextmanager
def in_directory(path):
    old = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


def read_book(teacher):
    ending = "教師版" if teacher else "學生版"
    return json.loads(next(WEEK.glob(f"*Vision_課堂簡化版_修訂版_{ending}.ipynb")).read_text(encoding="utf-8"))


def functions(teacher=True, path=None):
    path = path or PACKAGE / ("teacher" if teacher else "student") / "app.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    nodes = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))
             or (isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id.isupper())]
    namespace = {"__file__": str(path)}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


def rejects(call, kind=ValueError):
    try:
        call()
    except kind:
        return
    raise AssertionError("沒有拒絕不合格輸入")


def sample_folder(folder):
    """Notebook從week12開啟時的樣子：範例在week12_vision_revised/sample_data。"""
    target = Path(folder) / "week12_vision_revised/sample_data"
    target.mkdir(parents=True, exist_ok=True)
    for name in BUILD["SAMPLES"]:
        shutil.copyfile(PACKAGE / "sample_data" / name, target / name)


def check_samples():
    for name in BUILD["SAMPLES"]:
        assert (PACKAGE / "sample_data" / name).read_bytes() == (WEEK / "week12_vision_simple/sample_data" / name).read_bytes(), name
    manifest = json.loads((PACKAGE / "sample_data/fixture_manifest.json").read_text(encoding="utf-8"))
    assert manifest["receipt_clear.png"]["total"] == 300 and manifest["receipt_missing_total.png"]["total"] is None
    print("範例：兩張圖與人工基準和原簡化版逐位元相同通過")


SHARED = {
    "prepare": ["prepare_image"], "a": ["build_image_content"], "content-preview": ["summarize_content"],
    "answer": ["read_answer", "ask_vision"], "schema": ["read_receipt"],
}


def check_notebooks():
    books = [read_book(False), read_book(True)]
    assert [c["id"] for c in books[0]["cells"]] == [c["id"] for c in books[1]["cells"]]
    for s, t in zip(books[0]["cells"], books[1]["cells"]):
        if s["id"] not in [PREFIX + "cover", PREFIX + "a", PREFIX + "b-reference"]:
            assert s == t, s["id"]
    for teacher, book in zip([False, True], books):
        cells = book["cells"]
        assert len(cells) == 33 and len(cells) == len({c["id"] for c in cells})
        by_id = {c["id"].removeprefix(PREFIX): c for c in cells}
        namespace = {}
        with tempfile.TemporaryDirectory(dir=TEMP) as folder:
            sample_folder(folder)
            with in_directory(folder):
                for cell in cells:
                    text = "".join(cell["source"])
                    assert "�" not in text and "???" not in text and "原教材保留" not in text and "原版保留" not in text
                    if cell["cell_type"] == "markdown":
                        plain = re.sub(r"```.*?```", "", text, flags=re.S)
                        headings = re.findall(r"^#{1,6} .+", plain, re.M)
                        assert not headings or (len(headings) == 1 and text.startswith("#")), cell["id"]
                        assert not re.search(r"^ {4,}\S", plain, re.M), cell["id"]
                        continue
                    assert cell["outputs"] == [] and cell["execution_count"] is None
                    first_line = text.splitlines()[0]
                    assert first_line.startswith("# 用途：") and "先備：" in first_line, cell["id"]
                    for dependency in cell["metadata"]["teaching"]["requires"]:
                        assert dependency in by_id, dependency
                    ast.parse(text)
                    with redirect_stdout(StringIO()):
                        exec(text, namespace)
                    fresh = {}
                    for dependency in cell["metadata"]["teaching"]["requires"]:
                        with redirect_stdout(StringIO()):
                            exec("".join(by_id[dependency]["source"]), fresh)
                    with redirect_stdout(StringIO()):
                        exec(text, fresh)
        for name in ["qa_results", "qa_error", "receipt_results", "receipt_error", "teacher_record", "compare_rows"]:
            assert namespace[name] is None, name
        assert namespace["sample_image"]["width"] == 1000
        assert (namespace["content_result"] is not None) == teacher
        assert (namespace["content_preview"] is not None) == teacher
        if teacher:
            assert "（共" in namespace["content_preview"][1]["image_url"] and len(namespace["content_preview"][1]["image_url"]) < 80
        assert ("raise NotImplementedError" in "".join(by_id["a"]["source"])) != teacher
        ending = "教師版" if teacher else "學生版"
        reading = next(WEEK.glob(f"*Vision_課堂簡化版_修訂版_{ending}.md")).read_text(encoding="utf-8")
        for cell in cells:
            assert "".join(cell["source"]) in reading
        app_tree = ast.parse((PACKAGE / ("teacher" if teacher else "student") / "app.py").read_text(encoding="utf-8"))
        for tag, names in SHARED.items():
            cell_tree = ast.parse("".join(by_id[tag]["source"]))
            for name in names:
                node = next(n for n in cell_tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
                actual = next(n for n in app_tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
                assert ast.dump(node) == ast.dump(actual), name
        for tag, name in [("answer", "INSTRUCTIONS"), ("answer", "RECEIPT_PROMPT"), ("schema", "RECEIPT_SCHEMA")]:
            node = next(n for n in ast.parse("".join(by_id[tag]["source"])).body
                        if isinstance(n, ast.Assign) and n.targets[0].id == name)
            actual = next(n for n in app_tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == name)
            assert ast.dump(node) == ast.dump(actual), name
    # Colab：範例只在目前資料夾也找得到
    with tempfile.TemporaryDirectory(dir=TEMP) as folder:
        shutil.copyfile(PACKAGE / "sample_data/receipt_clear.png", Path(folder) / "receipt_clear.png")
        with in_directory(folder):
            ns = {}
            with redirect_stdout(StringIO()):
                exec("".join(by_id["prepare"]["source"]), ns)
                exec("".join(by_id["preview"]["source"]), ns)
            assert ns["find_sample"]("receipt_clear.png") == Path("receipt_clear.png") and ns["sample_image"]
            assert ns["find_sample"]("receipt_missing_total.png") is None
    print(f"Notebook：雙版各{len(books[0]['cells'])}格，JSON／ID／輸出／用途與先備／Markdown無意外縮排／AST／先備獨立與順序／"
          "答案分離／送出前預覽／App函式與規則常數對齊／App資料夾與Colab兩種範例位置通過")


def image_bytes(fmt, size=(30, 20), **kwargs):
    out = BytesIO()
    Image.new("RGB", size, "red").save(out, format=fmt, **kwargs)
    return out.getvalue()


def check_images_and_content():
    ns = functions()
    prepare, build, summarize = ns["prepare_image"], ns["build_image_content"], ns["summarize_content"]
    for fmt in ["PNG", "JPEG", "WEBP", "GIF"]:
        raw = image_bytes(fmt)
        img = prepare(raw)
        assert img["mime_type"] == "image/png" and img["original_format"] == fmt
        assert img["original_sha256"] == hashlib.sha256(raw).hexdigest()
        assert img["sent_sha256"] == hashlib.sha256(img["bytes"]).hexdigest()
        before = dict(img)
        content = build(img, "  What is visible?  ", "high")
        assert before == img and content[0] == {"type": "input_text", "text": "What is visible?"}
        assert base64.b64decode(content[1]["image_url"].split(",")[1]) == img["bytes"]
        copy = json.loads(json.dumps(content))
        short = summarize(content)
        assert content == copy and short[0] == content[0] and short[1]["image_url"].endswith("字元）")
    assert summarize([{"type": "input_image", "image_url": "https://example.com/a.png"}])[0]["image_url"] == "https://example.com/a.png"
    for raw in [b"", b"fake.png", b"A" * (2 * 1024 * 1024 + 1), image_bytes("BMP"), image_bytes("PNG", (2049, 20)), image_bytes("PNG")[:40]]:
        rejects(lambda raw=raw: prepare(raw))
    for fmt in ["GIF", "PNG", "WEBP"]:
        out = BytesIO()
        Image.new("RGB", (10, 10), "red").save(out, format=fmt, save_all=True,
                                               append_images=[Image.new("RGB", (10, 10), "blue")], duration=100)
        rejects(lambda: prepare(out.getvalue()))
    exif = Image.Exif()
    exif[274], exif[315] = 6, "fictional-metadata"
    img = prepare(image_bytes("JPEG", exif=exif))
    assert (img["width"], img["height"]) == (20, 30)
    with Image.open(BytesIO(img["bytes"])) as decoded:
        assert not decoded.getexif() and "exif" not in decoded.info
    out = BytesIO()
    Image.new("RGBA", (5, 5), (255, 0, 0, 0)).save(out, format="PNG")
    with Image.open(BytesIO(prepare(out.getvalue())["bytes"])) as decoded:
        assert decoded.getpixel((0, 0)) == (255, 255, 255)
    noisy = Image.frombytes("RGB", (1600, 1600), random.Random(12).randbytes(1600 * 1600 * 3))
    out = BytesIO()
    noisy.save(out, format="JPEG", quality=25)
    assert len(out.getvalue()) < 2 * 1024 * 1024
    rejects(lambda: prepare(out.getvalue()))
    img = prepare(image_bytes("PNG"))
    for question in ["", "  ", "a" * 301]:
        rejects(lambda question=question: build(img, question))
    rejects(lambda: build(img, "ok", "unknown"))
    rejects(lambda: functions(False)["build_image_content"](img, "ok"), NotImplementedError)
    check = ns["read_receipt"]
    assert check(json.dumps(RECEIPT)) == RECEIPT
    assert check(json.dumps(dict(RECEIPT, total=None, warnings=["沒有總額行"])))["total"] is None
    for value in [True, -1, float("nan"), float("inf"), "300"]:
        rejects(lambda value=value: check(json.dumps(dict(RECEIPT, total=value))))
    for item in [{}, [], dict(RECEIPT, extra=1), dict(RECEIPT, merchant=" "), dict(RECEIPT, visible_text=[]),
                 dict(RECEIPT, warnings="none"), dict(RECEIPT, total=None), dict(RECEIPT, visible_text=[1])]:
        rejects(lambda item=item: check(json.dumps(item)))
    rejects(lambda: check("not JSON"))
    print("圖片與A：真實四格式／動畫／大小／損壞／EXIF／metadata／白底／轉換後上限、Base64還原、content摘要不改原資料、Schema缺值與型別通過")


class Backend:
    """只攔截HTTP，不連線；不放進學生教材。"""
    def __init__(self):
        self.calls, self.options = [], []
        self.mode = "good"

    def handle(self, request):
        assert request.url.path == "/v1/responses", request.url
        body = json.loads(request.content)
        self.calls.append(body)
        if self.mode == "429":
            return httpx.Response(429, json={"error": {"message": "offline limit", "type": "rate_limit_error", "code": "rate_limit_exceeded"}})
        if self.mode == "timeout":
            raise httpx.ReadTimeout("offline timeout", request=request)
        result = dict(RECEIPT)
        if self.mode == "missing":
            result.update(total=None, warnings=["圖中未提供總額"])
        if self.mode == "bad-fields":
            result.pop("date")
        if self.mode == "bad-number":
            result["total"] = True
        answer = json.dumps(result) if "text" in body else "圖片可見Date: 2026-11-11及TOTAL TWD 300；老闆姓名無法確認。"
        if self.mode == "bad-json":
            answer = "not JSON"
        if self.mode == "empty":
            answer = "  "
        content = [{"type": "output_text", "text": answer, "annotations": []}]
        if self.mode == "refusal":
            content = [{"type": "refusal", "refusal": "offline refusal"}]
        response = {
            "id": "resp_offline", "object": "response", "created_at": 1,
            "status": "incomplete" if self.mode == "incomplete" else "completed",
            "model": "gpt-5.4-mini", "error": None,
            "output": [{"id": "msg_offline", "type": "message", "role": "assistant", "status": "completed", "content": content}],
            "usage": {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150,
                      "input_tokens_details": {"cached_tokens": 0}, "output_tokens_details": {"reasoning_tokens": 0}},
        }
        if self.mode == "no-status":
            response.pop("status")
        return httpx.Response(200, json=response)

    def client(self, **kwargs):
        self.options.append(kwargs)
        assert kwargs["max_retries"] == 0 and kwargs["timeout"] == 60
        return REAL_OPENAI(http_client=httpx.Client(transport=httpx.MockTransport(self.handle)), **kwargs)


def check_notebook_api():
    backend = Backend()
    teacher = {c["id"].removeprefix(PREFIX): "".join(c["source"]) for c in read_book(True)["cells"]}
    student_a = "".join(next(c for c in read_book(False)["cells"] if c["id"] == PREFIX + "a")["source"])
    requires = {c["id"].removeprefix(PREFIX): c["metadata"]["teaching"]["requires"] for c in read_book(True)["cells"]}

    def run(tag, mode="good", paid=True, key="offline-test-placeholder", student=False):
        backend.mode = mode
        backend.calls.clear()
        flag = {"qa-run": "RUN_VISION_API", "receipt-run": "RUN_RECEIPT_API"}[tag]
        ns = {}
        with patch.object(openai, "OpenAI", backend.client), patch("dotenv.load_dotenv"), \
                patch.dict(os.environ, {"OPENAI_API_KEY": key}), redirect_stdout(StringIO()):
            for dep in requires[tag]:
                exec(student_a if (dep == "a" and student) else teacher[dep], ns)
            exec(teacher[tag].replace(f"{flag} = False", f"{flag} = {paid}"), ns)
        return ns

    with tempfile.TemporaryDirectory(dir=TEMP) as folder:
        sample_folder(folder)
        with in_directory(folder):
            # 圖片問答：2題各1次
            assert run("qa-run", paid=False)["qa_results"] is None and not backend.calls
            assert run("qa-run", student=True)["qa_error"] and not backend.calls
            assert "OPENAI_API_KEY" in run("qa-run", key="")["qa_error"] and not backend.calls
            ns = run("qa-run")
            items = ns["qa_results"]["items"]
            assert len(backend.calls) == 2 and all(i["answer"] and i["usage"] for i in items)
            assert [c["input"][0]["content"][0]["text"] for c in backend.calls] == ns["QA_QUESTIONS"]
            sent = base64.b64decode(backend.calls[0]["input"][0]["content"][1]["image_url"].split(",")[1])
            assert hashlib.sha256(sent).hexdigest() == ns["qa_results"]["image_sha256"]
            body = backend.calls[0]
            assert body["store"] is False and body["max_output_tokens"] == 1200 and "text" not in body and "tools" not in body
            for mode in ["refusal", "incomplete", "no-status", "empty"]:
                items = run("qa-run", mode)["qa_results"]["items"]
                assert len(backend.calls) == 2 and all(i["answer"] is None and i["error"] for i in items), mode
            for mode in ["429", "timeout"]:
                ns = run("qa-run", mode)
                assert ns["qa_results"] is None and ns["qa_error"] and len(backend.calls) == 1, mode
            # 收據抽取：2張圖各1次
            ns = run("receipt-run")
            items = ns["receipt_results"]["items"]
            assert len(backend.calls) == 2 and [i["image"] for i in items] == ["receipt_clear.png", "receipt_missing_total.png"]
            assert all(i["result"] == RECEIPT for i in items)
            assert backend.calls[0]["text"]["format"]["strict"] is True
            assert run("receipt-run", "missing")["receipt_results"]["items"][1]["result"]["total"] is None
            for mode in ["bad-json", "bad-fields", "bad-number", "refusal", "incomplete", "empty"]:
                items = run("receipt-run", mode)["receipt_results"]["items"]
                assert len(backend.calls) == 2 and all(i["result"] is None and i["error"] for i in items), mode
            for mode in ["429", "timeout"]:
                ns = run("receipt-run", mode)
                assert ns["receipt_results"] is None and ns["receipt_error"] and len(backend.calls) == 1, mode
            assert run("receipt-run", student=True)["receipt_error"] and not backend.calls
            # 教師紀錄→讀回→逐欄對照
            qa_ns, receipt_ns = run("qa-run"), run("receipt-run")
            ns = {}
            with redirect_stdout(StringIO()):
                exec(teacher["prepare"], ns)
                ns.update(qa_results=qa_ns["qa_results"], receipt_results=receipt_ns["receipt_results"])
                exec(teacher["save-record"].replace("SAVE_TEACHER_RECORD = False", "SAVE_TEACHER_RECORD = True"), ns)
                saved = Path("teacher_vision_record.json").read_text(encoding="utf-8")
                assert "offline-test-placeholder" not in saved and "base64" not in saved
                fresh = {}
                exec(teacher["prepare"], fresh)
                exec(teacher["teacher-record-run"], fresh)
                assert fresh["teacher_record"]["receipts"] == json.loads(json.dumps(receipt_ns["receipt_results"]))
                fresh["receipt_results"] = None
                exec(teacher["b-compare"], fresh)
            rows = {(r["image"], r["field"]): r["same"] for r in fresh["compare_rows"]}
            assert rows[("receipt_clear.png", "total")] is True
            assert rows[("receipt_missing_total.png", "total")] is False   # 模擬回300：應被標成「不同：回看原圖」
            Path("teacher_vision_record.json").unlink()
    # 網址與file_id形狀只驗證序列化，不讀網址或檔案
    ns = {}
    with redirect_stdout(StringIO()):
        exec(teacher["transport-shapes"], ns)
    with backend.client(api_key="offline-test-placeholder", max_retries=0, timeout=60) as client:
        backend.mode = "good"
        for sample in [ns["url_content"], ns["file_content"]]:
            client.responses.create(model="gpt-5.4-mini", input=[{"role": "user", "content": sample}], store=False)
            assert backend.calls[-1]["input"][0]["content"] == sample
    print("Notebook API：真實SDK＋MockTransport驗證問答2題／抽取2張各1次、送出圖與SHA一致、A與缺key付費前阻擋、"
          "單題檢查失敗只記該題、429／逾時整批不存且不重試、教師紀錄存讀、逐欄對照標出補造、兩種傳輸形狀通過")


def check_apps():
    backend, downloads = Backend(), []

    def download(label, data, *args, **kwargs):
        downloads.append(json.loads(data))
        return False

    def submit(at):
        downloads.clear()
        at.button[1].click().run()
        assert not at.exception, at.exception

    with tempfile.TemporaryDirectory(dir=TEMP) as folder:
        target = Path(folder)
        shutil.copytree(PACKAGE, target, dirs_exist_ok=True)
        with patch.object(openai, "OpenAI", backend.client), patch.object(st, "secrets", {}), \
                patch.object(st, "download_button", download), patch("dotenv.load_dotenv"), \
                patch.dict(os.environ, {"OPENAI_API_KEY": "offline-test-placeholder"}):
            at = AppTest.from_file(str(target / "teacher/app.py"), default_timeout=25).run()
            assert not at.exception and not backend.calls
            submit(at)
            preview = at.session_state["preview"]
            assert preview and at.session_state["result"] is None and not backend.calls and not downloads
            assert preview["content"][0]["type"] == "input_text" and "（共" in preview["content"][1]["image_url"]
            assert at.info   # 提示只完成本機檢查
            at.checkbox[0].check().run()
            with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
                submit(at)
                assert at.error and not backend.calls
            submit(at)
            assert len(backend.calls) == 1 and downloads[-1]["task"] == "圖片問答"
            record = at.session_state["result"]
            sent = at.session_state["preview"]["bytes"]
            assert record["image"]["sent_sha256"] == hashlib.sha256(sent).hexdigest()
            assert base64.b64decode(backend.calls[-1]["input"][0]["content"][1]["image_url"].split(",")[1]) == sent
            assert "bytes" not in record["image"] and "base64" not in json.dumps(record)
            assert "offline-test-placeholder" not in json.dumps(record)
            before = len(backend.calls)
            at.run()
            assert len(backend.calls) == before and at.session_state["result"] == record
            for task in ["圖片問答", "收據抽取"]:
                at.selectbox[0].select(task).run()
                assert bool(at.text_area) == (task == "圖片問答")   # 收據抽取不顯示問題欄
                modes = ["refusal", "incomplete", "no-status", "empty", "429", "timeout"]
                if task == "收據抽取":
                    modes += ["bad-json", "bad-fields", "bad-number"]
                for mode in modes:
                    backend.mode = "good"
                    submit(at)
                    assert at.session_state["result"]
                    backend.mode = mode
                    before = len(backend.calls)
                    submit(at)
                    assert at.error and not downloads and at.session_state["result"] is None
                    assert len(backend.calls) == before + 1, (task, mode)
            backend.mode = "good"
            submit(at)
            assert backend.calls[-1]["input"][0]["content"][0]["text"] == BUILD_PROMPT()
            backend.mode = "missing"
            at.selectbox[1].select("缺少總額範例").run()
            submit(at)
            assert downloads[-1]["result"]["total"] is None and downloads[-1]["result"]["warnings"]
            assert backend.calls[-1]["text"]["format"]["strict"] is True
            at.selectbox[0].select("圖片問答").run()
            assert at.session_state["result"] is None
            for question in ["", "q" * 301]:
                at.text_area[0].set_value(question)
                before = len(backend.calls)
                submit(at)
                assert at.error and len(backend.calls) == before and not downloads
            at.text_area[0].set_value("日期為何？")
            at.selectbox[1].select("上傳自己的圖片").run()
            before = len(backend.calls)
            submit(at)
            assert at.error and len(backend.calls) == before
            # AppTest沒有原生上傳操作：替代上傳器，仍走真實圖片檢查與API流程
            supplied = SimpleNamespace(name="renamed.jpg", getvalue=lambda: image_bytes("PNG"))
            with patch.object(st, "file_uploader", return_value=supplied):
                backend.mode = "good"
                submit(at)
                assert at.session_state["result"]
                supplied.getvalue = lambda: b"not an image"
                submit(at)
                assert at.error and not downloads and at.session_state["result"] is None
            at.selectbox[1].select("清楚收據範例").run()
            submit(at)
            assert at.session_state["result"]
            before = len(backend.calls)
            at.button[0].click().run()
            assert at.session_state["result"] is None and len(backend.calls) == before
            submit(at)
            before = len(backend.calls)
            at.checkbox[0].uncheck().run()
            assert at.session_state["result"] is None and len(backend.calls) == before

            student = AppTest.from_file(str(target / "student/app.py"), default_timeout=25).run()
            assert not student.exception
            student.checkbox[0].check().run()
            before = len(backend.calls)
            submit(student)
            assert student.error and len(backend.calls) == before
            source = (target / "student/app.py").read_text(encoding="utf-8")
            assert BUILD["A_STUDENT"] in source
            path = target / "student/completed.py"
            path.write_text(source.replace(BUILD["A_STUDENT"], BUILD["A_TEACHER"]), encoding="utf-8")
            done = AppTest.from_file(str(path), default_timeout=25).run()
            submit(done)
            assert done.session_state["preview"] and not done.error and len(backend.calls) == before
            done.checkbox[0].check().run()
            submit(done)
            assert done.session_state["result"] and len(backend.calls) == before + 1
    print("AppTest：雙版預設0次並顯示送出前預覽、收據抽取不顯示問題欄、只移入A即可、兩任務每次1請求、rerun 0次、未知值、"
          "送出圖與SHA一致、替代上傳、各種失敗／模式／清除移除舊結果與下載通過")


def BUILD_PROMPT():
    return functions(True)["RECEIPT_PROMPT"]


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
    # 實際從.env讀到金鑰：入口資料夾一份可用；App資料夾也有時以App資料夾優先
    with tempfile.TemporaryDirectory(dir=TEMP) as folder:
        target = Path(folder)
        shutil.copytree(PACKAGE, target, dirs_exist_ok=True)
        for files, expected in [({"teacher/.env": "from-entry-env"}, "from-entry-env"),
                                ({".env": "from-app-folder-env"}, "from-app-folder-env")]:
            for name, value in files.items():
                (target / name).write_text(f"OPENAI_API_KEY={value}\n", encoding="utf-8")
            os.environ.pop("OPENAI_API_KEY", None)
            try:
                with patch.object(st, "secrets", {}):
                    AppTest.from_file(str(target / "teacher/app.py"), default_timeout=25).run()
                    assert os.environ.get("OPENAI_API_KEY") == expected
            finally:
                os.environ.pop("OPENAI_API_KEY", None)
        # Notebook：從week12資料夾讀App資料夾的.env
        api_setup = "".join(next(c for c in read_book(False)["cells"] if c["id"] == PREFIX + "api-setup")["source"])
        prepare = "".join(next(c for c in read_book(False)["cells"] if c["id"] == PREFIX + "prepare")["source"])
        notebook_dir = target / "nb"
        (notebook_dir / "week12_vision_revised").mkdir(parents=True)
        (notebook_dir / "week12_vision_revised/.env").write_text("OPENAI_API_KEY=from-notebook-env\n", encoding="utf-8")
        try:
            with in_directory(notebook_dir):
                ns = {}
                exec(prepare, ns)
                exec(api_setup, ns)
                assert ns["notebook_setting"]("OPENAI_API_KEY") == "from-notebook-env"
        finally:
            os.environ.pop("OPENAI_API_KEY", None)
    deps = lambda path: [l for l in path.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    for folder in ("student", "teacher"):
        assert deps(PACKAGE / folder / "requirements.txt") == deps(PACKAGE / "requirements.txt")
    assert ".env" in (PACKAGE / ".gitignore").read_text(encoding="utf-8").splitlines()
    print("金鑰設定：Secrets優先、無secrets.toml時讀環境變數、App實際讀到App資料夾與入口資料夾的.env（前者優先）、"
          "Notebook讀App資料夾.env、入口同層requirements通過")


def check_rebuild_and_preservation():
    files = [*WEEK.glob("*修訂版_*.ipynb"), *WEEK.glob("*修訂版_*.md"),
             *(p for p in PACKAGE.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.name != "README.md")]
    before = {p: p.read_bytes() for p in files}
    subprocess.run([sys.executable, "-B", "-X", "utf8", str(ROOT / "scripts/build_week12_revised.py")], check=True, capture_output=True)
    assert all(p.read_bytes() == content for p, content in before.items())
    for path in [*WEEK.glob("*修訂版*.md"), PACKAGE / "README.md"]:
        text = path.read_text(encoding="utf-8")
        assert "�" not in text and "???" not in text
        assert len(re.findall(r"^```", text, re.M)) % 2 == 0
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if not target.startswith(("https://", "http://", "#")):
                assert (path.parent / target.split("#")[0]).exists(), (path, target)
    status = subprocess.run(["git", "status", "--porcelain", "--", "week12"], cwd=ROOT, capture_output=True,
                            text=True, encoding="utf-8", check=True).stdout
    changed = [line for line in status.splitlines() if line.strip()]
    assert all(line.startswith("??") for line in changed), changed
    print("重建一致、UTF-8、Markdown圍欄與本機連結、原第12週檔案無修改通過")


def main():
    check_samples()
    check_notebooks()
    check_images_and_content()
    check_notebook_api()
    check_apps()
    check_settings()
    check_rebuild_and_preservation()
    import importlib.metadata as md
    print("Runtime:", sys.version.split()[0],
          {n: md.version(n) for n in ("streamlit", "openai", "python-dotenv", "httpx", "pillow")})
    print("全部離線驗證通過；0次真實API，未測真實辨識品質、真人瀏覽器上傳、Colab、Cloud或試教。")


if __name__ == "__main__":
    main()
