"""第12週離線驗證：真實圖片解碼、SDK＋HTTP模擬與AppTest；0次真實API。"""
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
PACKAGE = WEEK / "week12_vision_simple"
TEMP = ROOT / "output/week12_simple_revision"
TEMP.mkdir(parents=True, exist_ok=True)
(TEMP / ".gitignore").write_text("*\n", encoding="utf-8")
tempfile.tempdir = str(TEMP.resolve())
REAL_OPENAI = openai.OpenAI
RECEIPT = {"merchant": "DEMO CAFE", "date": "2026-11-11", "total": 300, "visible_text": ["Date: 2026-11-11", "TOTAL TWD 300"], "warnings": []}


@contextmanager
def in_directory(path):
    old = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


def book(teacher):
    ending = "教師版" if teacher else "學生版"
    return json.loads(next(WEEK.glob(f"*課堂簡化版_{ending}.ipynb")).read_text(encoding="utf-8"))


def functions(teacher=True):
    path = PACKAGE / ("teacher" if teacher else "student") / "app.py"
    nodes = [n for n in ast.parse(path.read_text(encoding="utf-8")).body if isinstance(n, ast.FunctionDef)]
    namespace = {"Image": Image, "ImageOps": ImageOps, "BytesIO": BytesIO, "hashlib": hashlib, "base64": base64, "json": json, "math": math}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


def rejects(call, kind=ValueError):
    try:
        call()
    except kind:
        return
    raise AssertionError("沒有拒絕不合格輸入")


def check_books():
    books = [book(False), book(True)]
    assert [c["id"] for c in books[0]["cells"]] == [c["id"] for c in books[1]["cells"]]
    for s, t in zip(books[0]["cells"], books[1]["cells"]):
        if s["id"] not in ["w12s-cover", "w12s-a", "w12s-teacher-note"]:
            assert s == t, s["id"]
    with tempfile.TemporaryDirectory(dir=TEMP) as folder:
        for p in (PACKAGE / "sample_data").glob("*.png"):
            shutil.copyfile(p, Path(folder) / p.name)
        with in_directory(folder):
            for teacher, b in zip([False, True], books):
                assert len(b["cells"]) == len({c["id"] for c in b["cells"]}) == 26
                tags = {c["id"].removeprefix("w12s-"): c for c in b["cells"]}
                namespace = {}
                for c in b["cells"]:
                    source = "".join(c["source"])
                    assert "\ufffd" not in source and "???" not in source
                    if c["cell_type"] == "markdown":
                        headings = re.findall(r"^#{1,6} .+", source, re.M)
                        assert len(headings) == 1 and source.startswith("#"), c["id"]
                        continue
                    ast.parse(source)
                    assert c["execution_count"] is None and c["outputs"] == []
                    with redirect_stdout(StringIO()):
                        exec(source, namespace)
                    fresh = {}
                    for dependency in c["metadata"]["teaching"]["requires"]:
                        with redirect_stdout(StringIO()):
                            exec("".join(tags[dependency]["source"]), fresh)
                    with redirect_stdout(StringIO()):
                        exec(source, fresh)
                assert namespace["qa_result"] is namespace["receipt_result"] is None
                assert namespace["qa_error"] is namespace["receipt_error"] is None
                assert (namespace["content_result"] is not None) == teacher
                ending = "教師版" if teacher else "學生版"
                reading = next(WEEK.glob(f"*課堂簡化版_{ending}.md")).read_text(encoding="utf-8")
                for c in b["cells"]:
                    assert "".join(c["source"]) in reading
                app_source = (PACKAGE / ("teacher" if teacher else "student") / "app.py").read_text(encoding="utf-8")
                app_tree = ast.parse(app_source)
                for tag, name in [("prepare", "prepare_image"), ("a", "build_image_content"), ("answer", "read_answer"), ("schema", "read_receipt")]:
                    node = next(n for n in ast.parse("".join(tags[tag]["source"])).body if isinstance(n, ast.FunctionDef) and n.name == name)
                    actual = next(n for n in app_tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
                    assert ast.dump(node) == ast.dump(actual)
    print("Notebook：雙版各26格（15文字／11程式），結構／ID／清空輸出／AST／先備獨立與順序／答案分離／App及Markdown對齊通過")


def image_bytes(fmt, size=(30, 20), **kwargs):
    out = BytesIO()
    Image.new("RGB", size, "red").save(out, format=fmt, **kwargs)
    return out.getvalue()


def check_images_and_content():
    ns = functions()
    prepare, build = ns["prepare_image"], ns["build_image_content"]
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
    for raw in [b"", b"fake.png", b"A" * (2 * 1024 * 1024 + 1), image_bytes("BMP"), image_bytes("PNG", (2049, 20)), image_bytes("PNG")[:40]]:
        rejects(lambda raw=raw: prepare(raw))
    for fmt in ["GIF", "PNG", "WEBP"]:
        out = BytesIO()
        Image.new("RGB", (10, 10), "red").save(out, format=fmt, save_all=True, append_images=[Image.new("RGB", (10, 10), "blue")], duration=100)
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
    out = BytesIO(); noisy.save(out, format="JPEG", quality=25)
    assert len(out.getvalue()) < 2 * 1024 * 1024
    rejects(lambda: prepare(out.getvalue()))
    img = prepare(image_bytes("PNG"))
    for question in ["", "  ", "a" * 301]:
        rejects(lambda question=question: build(img, question))
    rejects(lambda: build(img, "ok", "unknown"))
    rejects(lambda: functions(False)["build_image_content"](img, "ok"), NotImplementedError)
    check = ns["read_receipt"]
    assert check(json.dumps(RECEIPT)) == RECEIPT
    missing = dict(RECEIPT, total=None, warnings=["沒有總額行"])
    assert check(json.dumps(missing))["total"] is None
    for value in [True, -1, float("nan"), float("inf"), "300"]:
        rejects(lambda value=value: check(json.dumps(dict(RECEIPT, total=value))))
    for item in [{}, [], dict(RECEIPT, extra=1), dict(RECEIPT, merchant=" "), dict(RECEIPT, visible_text=[]), dict(RECEIPT, warnings="none"), dict(RECEIPT, total=None), dict(RECEIPT, visible_text=[1])]:
        rejects(lambda item=item: check(json.dumps(item)))
    rejects(lambda: check("not JSON"))
    print("圖片與A：真實四格式／動畫及多影格／大小／損壞／EXIF方向／metadata／白底／轉換後上限、傳輸還原與Schema缺值型別通過")


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
        if self.mode == "bad-fields": result.pop("date")
        if self.mode == "bad-number": result["total"] = True
        answer = json.dumps(result) if "text" in body else "圖片可見Date: 2026-11-11及TOTAL TWD 300；老闆姓名無法確認。"
        if self.mode == "bad-json": answer = "not JSON"
        if self.mode == "empty": answer = "  "
        content = [{"type": "output_text", "text": answer, "annotations": []}]
        if self.mode == "refusal": content = [{"type": "refusal", "refusal": "offline refusal"}]
        response = {
            "id": "resp_offline", "object": "response", "created_at": 1,
            "status": "incomplete" if self.mode == "incomplete" else "completed",
            "model": "gpt-5.4-mini", "error": None,
            "output": [{"id": "msg_offline", "type": "message", "role": "assistant", "status": "completed", "content": content}],
            "usage": {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150,
                      "input_tokens_details": {"cached_tokens": 0}, "output_tokens_details": {"reasoning_tokens": 0}},
        }
        if self.mode == "no-status": response.pop("status")
        return httpx.Response(200, json=response)

    def client(self, **kwargs):
        self.options.append(kwargs)
        assert kwargs["max_retries"] == 0 and kwargs["timeout"] == 60
        return REAL_OPENAI(http_client=httpx.Client(transport=httpx.MockTransport(self.handle)), **kwargs)


def check_notebook_api():
    backend = Backend()
    with tempfile.TemporaryDirectory(dir=TEMP) as folder:
        shutil.copyfile(PACKAGE / "sample_data/receipt_clear.png", Path(folder) / "receipt_clear.png")
        with in_directory(folder), patch.object(openai, "OpenAI", backend.client), patch("dotenv.load_dotenv"), patch.dict(os.environ, {"OPENAI_API_KEY": "offline-placeholder"}):
            tags = {c["id"].removeprefix("w12s-"): "".join(c["source"]) for c in book(True)["cells"]}
            for tag, flag, result in [("qa-run", "RUN_VISION_API", "qa_result"), ("receipt-run", "RUN_RECEIPT_API", "receipt_result")]:
                ns = {}
                for dependency in ["prepare", "a", "answer", "schema"]: exec(tags[dependency], ns)
                with redirect_stdout(StringIO()): exec(tags[tag], ns)
                before = len(backend.calls)
                assert ns[result] is None
                active = tags[tag].replace(flag + " = False", flag + " = True")
                with redirect_stdout(StringIO()): exec(active, ns)
                assert ns[result] and len(backend.calls) == before + 1
                body = backend.calls[-1]
                assert body["store"] is False and body["max_output_tokens"] == 1200
                assert "tools" not in body and len(body["input"][0]["content"]) == 2
                modes = ["refusal", "incomplete", "no-status", "empty", "429", "timeout"]
                if tag == "receipt-run": modes += ["bad-json", "bad-fields", "bad-number"]
                for mode in modes:
                    backend.mode = mode
                    before = len(backend.calls)
                    with redirect_stdout(StringIO()): exec(active, ns)
                    assert ns[result] is None and len(backend.calls) == before + 1, mode
                    assert ns[result.replace("_result", "_error")]
                backend.mode = "good"
                before = len(backend.calls)
                with patch.dict(os.environ, {"OPENAI_API_KEY": ""}), redirect_stdout(StringIO()): exec(active, ns)
                assert ns[result] is None and len(backend.calls) == before
                student_a = next(c for c in book(False)["cells"] if c["id"] == "w12s-a")
                exec("".join(student_a["source"]), ns)
                with redirect_stdout(StringIO()): exec(active, ns)
                assert ns[result] is None and len(backend.calls) == before
            # 真實SDK只驗證三種傳輸序列化；MockTransport不讀網址或檔案ID。
            exec(tags["prepare"], ns); exec(tags["a"], ns); exec(tags["transport-shapes"], ns)
            content = ns["build_image_content"](ns["prepare_image"](Path("receipt_clear.png").read_bytes()), "test")
            with backend.client(api_key="offline-placeholder", max_retries=0, timeout=60) as client:
                for sample in [content, ns["url_content"], ns["file_content"]]:
                    client.responses.create(model="gpt-5.4-mini", input=[{"role": "user", "content": sample}], store=False)
                    assert backend.calls[-1]["input"][0]["content"] == sample
    print("Notebook API：真實SDK＋HTTP模擬0／1次、三種傳輸形狀、回應／解析／缺key／A未完／429／逾時不重試與清舊結果通過")


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
        with patch.object(openai, "OpenAI", backend.client), patch.object(st, "secrets", {}), patch.object(st, "download_button", download), patch("dotenv.load_dotenv"), patch.dict(os.environ, {"OPENAI_API_KEY": "offline-placeholder"}):
            at = AppTest.from_file(str(target / "teacher/app.py"), default_timeout=25).run()
            assert not at.exception and not backend.calls
            submit(at)
            assert at.session_state["preview"] and at.session_state["result"] is None and not backend.calls and not downloads
            at.checkbox[0].check().run()
            with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
                submit(at)
                assert at.error and not backend.calls
            submit(at)
            assert len(backend.calls) == 1 and downloads[-1]["task"] == "圖片問答"
            record = at.session_state["result"]
            image_bytes_sent = at.session_state["preview"]["bytes"]
            assert record["image"]["sent_sha256"] == hashlib.sha256(image_bytes_sent).hexdigest()
            body = backend.calls[-1]
            assert base64.b64decode(body["input"][0]["content"][1]["image_url"].split(",")[1]) == image_bytes_sent
            assert "bytes" not in record["image"] and "base64" not in json.dumps(record)
            before = len(backend.calls)
            at.run()
            assert len(backend.calls) == before and at.session_state["result"] == record
            for task in ["圖片問答", "收據抽取"]:
                at.selectbox[0].select(task).run()
                modes = ["refusal", "incomplete", "no-status", "empty", "429", "timeout"]
                if task == "收據抽取": modes += ["bad-json", "bad-fields", "bad-number"]
                for mode in modes:
                    backend.mode = "good"
                    submit(at)
                    assert at.session_state["result"]
                    backend.mode = mode
                    before = len(backend.calls)
                    submit(at)
                    assert at.error and not downloads and at.session_state["result"] is None and len(backend.calls) == before + 1, (task, mode)
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
            # AppTest未提供原生上傳操作，替代上傳器；仍走真實圖片驗證及API線。
            supplied = SimpleNamespace(name="renamed.jpg", getvalue=lambda: image_bytes("PNG"))
            with patch.object(st, "file_uploader", return_value=supplied):
                submit(at)
                assert at.session_state["result"]
                supplied.getvalue = lambda: b"not an image"
                submit(at)
                assert at.error and not downloads and at.session_state["result"] is None
            at.selectbox[1].select("清楚收據範例").run()
            backend.mode = "good"
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
            answer = (target / "teacher/app.py").read_text(encoding="utf-8")
            node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "build_image_content")
            answer_node = next(n for n in ast.parse(answer).body if isinstance(n, ast.FunctionDef) and n.name == "build_image_content")
            lines = source.splitlines(keepends=True)
            completed = "".join(lines[:node.lineno-1]) + ast.get_source_segment(answer, answer_node) + "\n" + "".join(lines[node.end_lineno:])
            path = target / "student/completed.py"
            path.write_text(completed, encoding="utf-8")
            done = AppTest.from_file(str(path), default_timeout=25).run()
            submit(done)
            assert done.session_state["preview"] and not done.error and len(backend.calls) == before
            done.checkbox[0].check().run()
            submit(done)
            assert done.session_state["result"] and len(backend.calls) == before + 1
    print("AppTest：雙版預設0次、移入A成功、兩任務1次／rerun0次、未知值、真實傳送圖與SHA、替代上傳、錯誤／模式／清除與舊下載清除通過")


def check_preservation():
    paths = list(WEEK.glob("*課堂簡化版_*.ipynb")) + list(WEEK.glob("*課堂簡化版_*.md")) + [p for p in PACKAGE.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    saved = {p: p.read_bytes() for p in paths}
    subprocess.run([sys.executable, "-B", "-X", "utf8", str(ROOT / "scripts/build_week12_simple.py")], check=True, capture_output=True)
    assert all(p.read_bytes() == data for p, data in saved.items())
    docs = list(WEEK.glob("*課堂簡化版*.md")) + list(PACKAGE.rglob("*.md"))
    for p in docs:
        text = p.read_text(encoding="utf-8")
        assert "\ufffd" not in text and "???" not in text and len(re.findall(r"^```", text, re.M)) % 2 == 0
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if not target.startswith(("https://", "http://", "#")):
                assert (p.parent / target.split("#")[0]).exists(), (p, target)
    for p in [ROOT / "scripts/build_week12_simple.py", Path(__file__), *PACKAGE.rglob("*.py")]:
        ast.parse(p.read_text(encoding="utf-8"))
    baseline_path = TEMP / "before.json"
    if baseline_path.exists():
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        for name, checksum in baseline.items():
            if name == "PROJECT_MEMORY.md": continue
            assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == checksum, name
        print(f"重建／連結／語法與工作前{len(baseline)-1}份原檔含第9～11週成果保留通過")
    else:
        print("重建／連結／語法通過；本機工作前雜湊紀錄不存在，未執行原檔保留比對")


def main():
    check_books()
    check_images_and_content()
    check_notebook_api()
    check_apps()
    check_preservation()
    print("全部離線驗證通過；0次真實API，未測真實辨識／瀏覽器上傳／Cloud／Colab或試教。")


if __name__ == "__main__":
    main()
