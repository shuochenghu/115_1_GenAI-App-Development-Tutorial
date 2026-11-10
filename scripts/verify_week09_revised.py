"""第9週修訂版教師驗證：本機文件、Notebook與AppTest；不發送真實API請求。"""

import ast
from contextlib import redirect_stdout
import hashlib
from io import BytesIO, StringIO
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import tempfile
from types import SimpleNamespace, ModuleType
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
WEEK = ROOT / "week09"
PACKAGE = WEEK / "week09_document_revised"
SAMPLES = PACKAGE / "sample_data"
PREFIX = "w09r-"
TEMP = ROOT / "output/week09_revised_checks"
TEMP.mkdir(parents=True, exist_ok=True)
(TEMP / ".gitignore").write_text("*\n", encoding="utf-8")
tempfile.tempdir = str(TEMP.resolve())
BUILD = runpy.run_path(str(ROOT / "scripts/build_week09_revised.py"))
from streamlit.testing.v1 import AppTest  # noqa: E402

for name in [k for k in os.environ if k.startswith("OPENAI_")]:
    del os.environ[name]


def read_book(teacher):
    ending = "教師版" if teacher else "學生版"
    return json.loads(next(WEEK.glob(f"*課堂簡化版_修訂版_{ending}.ipynb")).read_text(encoding="utf-8"))


def app_functions(teacher):
    source = (PACKAGE / ("teacher" if teacher else "student") / "app.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    nodes = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))]
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "app-functions", "exec"), namespace)
    return namespace


def expect_error(call, error=ValueError):
    try:
        call()
    except error:
        return
    raise AssertionError(f"未拒絕輸入，應為{error.__name__}")


def check_notebooks():
    student, teacher = read_book(False), read_book(True)
    reference = app_functions(True)
    assert [c["id"] for c in student["cells"]] == [c["id"] for c in teacher["cells"]]
    for s_cell, t_cell in zip(student["cells"], teacher["cells"]):
        if s_cell["id"] not in [PREFIX + "cover", PREFIX + "a", PREFIX + "b-result"]:
            assert s_cell == t_cell, s_cell["id"]
    for book, is_teacher in [(student, False), (teacher, True)]:
        cells = book["cells"]
        assert len(cells) == 49 and len({c["id"] for c in cells}) == len(cells)
        by_tag = {c["id"].removeprefix(PREFIX): c for c in cells}
        for missing_files in (False, True):
            sequential = {}
            with tempfile.TemporaryDirectory(dir=TEMP) as folder, patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
                if not missing_files:
                    for name in BUILD["SAMPLE_NAMES"]:
                        (Path(folder) / name).write_bytes((SAMPLES / name).read_bytes())
                old = Path.cwd()
                os.chdir(folder)
                try:
                    for cell in cells:
                        source = "".join(cell["source"])
                        assert "�" not in source and "???" not in source
                        if cell["cell_type"] == "markdown":
                            headings = re.findall(r"^#{1,6} .+", source, re.M)
                            if headings:
                                assert len(headings) == 1 and source.startswith("#"), cell["id"]
                            continue
                        assert cell["outputs"] == [] and cell["execution_count"] is None
                        assert source.startswith("# 用途：") and "先備：" in source.splitlines()[0], cell["id"]
                        ast.parse(source)
                        with redirect_stdout(StringIO()):
                            exec(compile(source, cell["id"], "exec"), sequential)
                        fresh = {}
                        for dependency in cell["metadata"]["teaching"]["requires"]:
                            with redirect_stdout(StringIO()):
                                exec("".join(by_tag[dependency]["source"]), fresh)
                        with redirect_stdout(StringIO()):
                            exec(source, fresh)
                        if missing_files:
                            continue
                        format_names = {"txt-demo": "sample.txt", "reader-demo": "sample.csv",
                                        "pdf-demo": "sample.pdf", "docx-demo": "sample.docx"}
                        tag = cell["id"].removeprefix(PREFIX)
                        if tag in format_names:
                            name = format_names[tag]
                            assert isinstance(fresh["data"], bytes)
                            assert fresh["raw_text"] == reference["extract_text"](name, fresh["data"], "utf-8-sig")
                        if tag == "integrate-run" and is_teacher:
                            raw = reference["extract_text"]("sample.txt", Path("sample.txt").read_bytes(), "utf-8-sig")
                            cleaned = reference["clean_text"](raw)
                            assert fresh["document_result"] == {
                                "filename": "sample.txt", "encoding": "utf-8-sig", "raw_text": raw,
                                "cleaned_text": cleaned, "character_count": len(cleaned),
                                "chunk_size": 120, "overlap": 20,
                                "chunks": reference["chunk_text"](cleaned, 120, 20),
                            }
                            # 文字格寫的預期數字要和實際結果一致
                            note = "".join(by_tag["integrate"]["source"])
                            assert f"清理後有{len(cleaned)}個字元、切成{len(fresh['document_result']['chunks'])}個片段" in note
                        if tag == "b-check":
                            first, second = fresh["comparison_result"]
                            assert [first["overlap"], second["overlap"]] == [0, 4]
                            assert len(first["chunks"]) == len(second["chunks"]) == 3
                            assert not any("圖書館討論室" in item["text"] for item in first["chunks"])
                            assert "地點是圖書館討論室" in second["chunks"][1]["text"]
                    assert sequential["summary_result"] is None and sequential["summary_error"] is None
                    if missing_files:
                        # 缺範例檔時每個讀檔格只提示、不中斷；整合格記錯誤
                        assert sequential["document_result"] is None and sequential["document_error"]
                    else:
                        assert (sequential["document_result"] is not None) == is_teacher
                finally:
                    os.chdir(old)
        ending = "教師版" if is_teacher else "學生版"
        reading = next(WEEK.glob(f"*課堂簡化版_修訂版_{ending}.md")).read_text(encoding="utf-8")
        app_tree = ast.parse((PACKAGE / ("teacher" if is_teacher else "student") / "app.py").read_text(encoding="utf-8"))
        for cell in cells:
            assert "".join(cell["source"]) in reading
        for tag, function in [("a", "clean_text"), ("b", "chunk_text"), ("reader-function", "extract_text")]:
            book_tree = ast.parse("".join(by_tag[tag]["source"]))
            expected = next(n for n in book_tree.body if isinstance(n, ast.FunctionDef))
            actual = next(n for n in app_tree.body if isinstance(n, ast.FunctionDef) and n.name == function)
            assert ast.dump(expected) == ast.dump(actual)
        a_source = "".join(by_tag["a"]["source"])
        assert ("raise NotImplementedError" in a_source) != is_teacher
        if not is_teacher:
            assert r"\n{3,}" not in a_source   # 學生版不直接給出答案的正規表示式
        for tag in ["txt-demo", "reader-demo", "pdf-demo", "docx-demo", "integrate-run"]:
            assert "sample_tata" not in "".join(by_tag[tag]["source"])
        bridge = "".join(by_tag["bridge"]["source"])
        assert "貼進第10週App" in bridge and "尚未製作" not in bridge and "留待後續課程" not in bridge
        for cell in cells:
            assert "新版另存" not in "".join(cell["source"])
    print(f"Notebook：雙版各{len(teacher['cells'])}格，JSON／ID／輸出／可見用途與先備／AST／先備獨立與順序／缺檔不中斷／閱讀版／答案分離、四格式與App一致通過")


def fixtures():
    """記憶體中的reader測試資料，不作為交付文件。"""
    from pypdf import PdfWriter
    from pypdf.generic import NameObject, DictionaryObject, DecodedStreamObject
    from docx import Document

    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=300)
    font = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    })
    page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})})
    stream = DecodedStreamObject()
    stream.set_data(b"BT /F1 12 Tf 20 200 Td (Club meeting 4 people) Tj ET")
    page[NameObject("/Contents")] = stream
    writer.add_blank_page(width=300, height=300)
    pdf_io = BytesIO()
    writer.write(pdf_io)
    blank_writer = PdfWriter()
    blank_writer.add_blank_page(width=300, height=300)
    blank_io = BytesIO()
    blank_writer.write(blank_io)
    encrypted_io = BytesIO()
    blank_writer.encrypt("classroom-only")
    blank_writer.write(encrypted_io)
    long_writer = PdfWriter()
    for _ in range(51):
        long_writer.add_blank_page(width=100, height=100)
    long_io = BytesIO()
    long_writer.write(long_io)
    document = Document()
    document.add_paragraph("段落前：活動日期10/28")
    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "人數"
    table.cell(0, 1).text = "4"
    document.add_paragraph("段落後：報名未公告")
    docx_io = BytesIO()
    document.save(docx_io)
    return {"pdf": pdf_io.getvalue(), "blank": blank_io.getvalue(), "encrypted": encrypted_io.getvalue(),
            "long": long_io.getvalue(), "docx": docx_io.getvalue()}


def check_functions(data):
    namespace = app_functions(True)
    clean, chunk, extract = [namespace[x] for x in ["clean_text", "chunk_text", "extract_text"]]
    assert clean("A  B\r\n\r\n\r\nC\t4。") == "A B\n\nC 4。"
    assert clean("第一段\n\n\n\n第二段") == "第一段\n\n第二段"
    for text in ["", " ", "A", "ABCDEFGHIJ", "中文日期10/28\n\n每組4人。", " A B C "]:
        for size in range(1, 8):
            for overlap in range(size):
                result = chunk(text, size, overlap)
                if not text.strip():
                    assert result == []
                    continue
                covered = set()
                for number, item in enumerate(result):
                    assert item["chunk_id"] == number
                    assert item["text"] == text[item["start"]:item["end"]]
                    assert 0 < len(item["text"]) <= size
                    covered.update(range(item["start"], item["end"]))
                assert all(i in covered for i, char in enumerate(text) if not char.isspace())
    for size, overlap in [(0, 0), (-1, 0), (4, -1), (4, 4), (4, 5)]:
        expect_error(lambda: chunk("A", size, overlap))
    for name in ["note.TXT", "note.md"]:
        assert extract(name, "中文4人".encode("utf-8-sig")) == "中文4人"
        assert extract(name, "中文4人".encode("cp950"), "cp950") == "中文4人"
    expect_error(lambda: extract("x.txt", "社團".encode("cp950")), UnicodeDecodeError)
    assert "地點=圖書館,討論室" in extract("x.csv", '活動,地點\n交流,"圖書館,討論室"\n'.encode())
    for csv_text in [",地點\n活動,A\n", "活動,活動\nA,B\n", "活動,地點\nA\n", "活動\nA,B\n"]:
        expect_error(lambda: extract("x.csv", csv_text.encode()))
    expect_error(lambda: extract("x.csv", ("活動\n" + "A\n" * 201).encode()))
    expect_error(lambda: extract("x.exe", b"A"))
    pdf_text = extract("fixture.pdf", data["pdf"])
    assert "Club meeting 4 people" in pdf_text and "[第2頁]" in pdf_text and "此頁無文字層" in pdf_text
    for name in ["blank", "encrypted", "long"]:
        expect_error(lambda: extract("fixture.pdf", data[name]))
    word_text = extract("fixture.docx", data["docx"])
    assert word_text.index("段落前") < word_text.index("人數 | 4") < word_text.index("段落後")
    expect_error(lambda: extract("broken.pdf", b"invalid"), Exception)
    expect_error(lambda: extract("broken.docx", b"invalid"), Exception)
    student_functions = app_functions(False)
    expect_error(lambda: student_functions["clean_text"]("學生未完成"), NotImplementedError)
    # 四個範例檔與原版sample_tata逐位元相同
    for name in BUILD["SAMPLE_NAMES"]:
        assert (SAMPLES / name).read_bytes() == (WEEK / "sample_tata" / name).read_bytes()
        assert extract(name, (SAMPLES / name).read_bytes()).strip()
    print("函式：清理、切塊邊界、UTF-8／CP950、CSV、PDF文字／空白／加密／頁數、DOCX順序、損壞檔、範例檔一致通過")


def check_apps(data):
    import streamlit as st
    downloads = []
    current = {"upload": None}

    def download(label, data, **kwargs):
        downloads.append((label, data))
        return False

    def last_json():
        return json.loads(next(d for label, d in reversed(downloads) if label.startswith("下載chunks JSON")))

    def submit(at):
        downloads.clear()
        next(b for b in at.button if b.label == "處理文件").click().run()
        assert not at.exception, at.exception

    with patch.object(st, "download_button", side_effect=download), \
            patch.object(st, "file_uploader", side_effect=lambda *a, **k: current["upload"]):
        teacher = AppTest.from_file(str(PACKAGE / "teacher/app.py"), default_timeout=20).run()
        assert not teacher.exception and not downloads
        # 內建範例：四個檔案都能處理，下載兩種檔案
        for name, expected in [("sample.txt", "總名額32人"), ("sample.csv", "活動=讀書交流"),
                               ("sample.pdf", "[第1頁]"), ("sample.docx", "|")]:
            teacher.selectbox[0].select(name)
            submit(teacher)
            assert len(downloads) == 2 and expected in last_json()["cleaned_text"], name
            cleaned_download = next(d for label, d in downloads if label.startswith("下載清理後文字"))
            assert cleaned_download == teacher.session_state["document_result"]["cleaned_text"]
        teacher.selectbox[0].select("sample.txt")
        submit(teacher)
        first = last_json()
        # 與Notebook整合格相同的資料與參數
        ns = app_functions(True)
        raw = ns["extract_text"]("sample.txt", (SAMPLES / "sample.txt").read_bytes())
        assert first["chunks"] == ns["chunk_text"](ns["clean_text"](raw), 120, 20)
        teacher.run()
        assert teacher.session_state["document_result"] == first
        teacher.number_input[0].set_value(0)
        submit(teacher)
        assert last_json()["overlap"] == 0
        teacher.number_input[0].set_value(120)
        submit(teacher)
        assert teacher.error and not downloads and teacher.session_state["document_result"] is None
        teacher.number_input[0].set_value(20)
        submit(teacher)
        assert downloads
        downloads.clear()
        next(b for b in teacher.button if b.label == "清除結果").click().run()
        assert teacher.session_state["document_result"] is None and not downloads

        # 上傳檔案
        teacher.radio[0].set_value("上傳檔案")
        submit(teacher)
        assert teacher.error and not downloads   # 沒選檔
        for filename, content, expected in [
            ("x.csv", (SAMPLES / "sample.csv").read_bytes(), "活動=讀書交流"),
            ("x.pdf", data["pdf"], "Club meeting"),
            ("x.docx", data["docx"], "段落前"),
            ("x.txt", "自備中文活動4人".encode(), "4人"),
        ]:
            current["upload"] = SimpleNamespace(name=filename, getvalue=lambda content=content: content)
            submit(teacher)
            assert downloads and expected in last_json()["cleaned_text"]
        for filename, content in [
            ("blank.txt", b"  \n"), ("long.txt", b"a" * 20001), ("large.txt", b"a" * (1024 * 1024 + 1)),
            ("blank.pdf", data["blank"]), ("broken.pdf", b"bad"), ("broken.docx", b"bad"),
            ("bad.csv", b"a,b\nx\n"), ("encoding.txt", "社團".encode("cp950")),
        ]:
            current["upload"] = SimpleNamespace(name="ok.txt", getvalue=lambda: b"valid input")
            submit(teacher)
            assert downloads
            current["upload"] = SimpleNamespace(name=filename, getvalue=lambda content=content: content)
            submit(teacher)
            assert teacher.error and not downloads and teacher.session_state["document_result"] is None
        current["upload"] = SimpleNamespace(name="cp950.txt", getvalue=lambda: "社團4人".encode("cp950"))
        teacher.selectbox[1].select("cp950")
        submit(teacher)
        assert last_json()["cleaned_text"] == "社團4人"
        current["upload"] = None

        student = AppTest.from_file(str(PACKAGE / "student/app.py"), default_timeout=20).run()
        submit(student)
        assert student.warning and not downloads and student.session_state["document_result"] is None

        # 學生只移入A即可成功
        student_source = (PACKAGE / "student/app.py").read_text(encoding="utf-8")
        assert BUILD["CLEAN_STUDENT"] in student_source
        completed = PACKAGE / "student/.verify_completed.py"
        try:
            completed.write_text(student_source.replace(BUILD["CLEAN_STUDENT"], BUILD["CLEAN"]), encoding="utf-8")
            completed_at = AppTest.from_file(str(completed), default_timeout=20).run()
            submit(completed_at)
            assert downloads and not completed_at.warning
            assert last_json()["chunks"] == first["chunks"]
        finally:
            completed.unlink(missing_ok=True)
    print("AppTest：雙版啟動、內建四範例、兩種下載、A未完成阻擋、只移入A即成功、上傳多格式、錯誤清舊結果、清除通過")


def check_api():
    source = "".join(next(c for c in read_book(True)["cells"] if c["id"] == PREFIX + "api")["source"])
    calls, client_settings = [], []
    state = {"response": None}
    fake_module = ModuleType("openai")

    class FakeClient:
        def __init__(self, **kwargs):
            client_settings.append(kwargs)
            self.responses = SimpleNamespace(create=self.create)

        def create(self, **kwargs):
            calls.append(kwargs)
            if isinstance(state["response"], Exception):
                raise state["response"]
            return state["response"]

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    fake_module.OpenAI = FakeClient

    def run(response, paid=True, key="offline-placeholder", input_override=None):
        calls.clear(); client_settings.clear()
        state["response"] = response
        activity = source.replace("RUN_PAID_API = False", f"RUN_PAID_API = {paid}")
        if input_override is not None:
            activity = activity.replace('summary_input = "社團下週三下午在圖書館討論室交流。報名方式尚未公告。"',
                                        "summary_input = " + repr(input_override))
        namespace = {"summary_result": "old-success"}
        with patch.dict(sys.modules, {"openai": fake_module}), patch("dotenv.load_dotenv"), \
                patch.dict(os.environ, {"OPENAI_API_KEY": key}), redirect_stdout(StringIO()):
            exec(activity, namespace)
        return namespace

    good = SimpleNamespace(status="completed", output_text="三個重點", output=[])
    assert run(good, paid=False)["summary_result"] is None and not calls
    assert run(good)["summary_result"] == "三個重點" and len(calls) == 1
    assert calls[0]["store"] is False and calls[0]["max_output_tokens"] == 1200
    assert client_settings[0]["max_retries"] == 0 and client_settings[0]["timeout"] == 60.0
    for response in [
        SimpleNamespace(status="incomplete", output_text="部分", output=[]),
        SimpleNamespace(status="failed", output_text="錯誤", output=[]),
        SimpleNamespace(status="completed", output_text=" ", output=[]),
        SimpleNamespace(status="completed", output_text="文字", output=[SimpleNamespace(type="message", content=[SimpleNamespace(type="refusal")])]),
        RuntimeError("offline network error"),
    ]:
        result = run(response)
        assert result["summary_result"] is None and result["summary_error"] and len(calls) == 1
    assert run(good, key="")["summary_error"] and not calls
    for text in [" ", "A" * 6001]:
        assert run(good, input_override=text)["summary_error"] and not calls
    print("選做API：假SDK驗證預設0次、有效最多1次、with關閉、參數、缺key／超長／拒答／未完成／空結果／失敗清舊資料通過")


def check_rebuild_and_links():
    targets = [*WEEK.glob("*修訂版_*.ipynb"), *WEEK.glob("*修訂版_*.md"), *PACKAGE.rglob("app.py"),
               *(SAMPLES / n for n in BUILD["SAMPLE_NAMES"])]
    before = {path: path.read_bytes() for path in targets}
    subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts/build_week09_revised.py")], check=True, capture_output=True)
    assert all(path.read_bytes() == content for path, content in before.items())
    docs = [*WEEK.glob("*修訂版*.md"), PACKAGE / "README.md", SAMPLES / "README.md"]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "�" not in text and "???" not in text
        assert len(re.findall(r"^```", text, re.M)) % 2 == 0
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if not target.startswith(("https://", "http://", "#")):
                assert (path.parent / target.split("#")[0]).exists(), (path, target)
    print("重建一致、範例檔複製一致、UTF-8、Markdown與本機連結通過")


def main():
    check_notebooks()
    data = fixtures()
    check_functions(data)
    check_apps(data)
    check_api()
    check_rebuild_and_links()
    import importlib.metadata as md
    print("Runtime:", sys.version.split()[0], {n: md.version(n) for n in ("streamlit", "pypdf", "python-docx", "openai")})
    print("全部離線驗證通過；0次真實API，未啟動伺服器，未測真人瀏覽器／Colab／Cloud／試教。")


if __name__ == "__main__":
    main()
