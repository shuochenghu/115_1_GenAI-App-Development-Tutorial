"""整合RAG離線驗證：實際讀檔、真實SDK＋MockTransport與AppTest；0次真實API。"""
import ast
from contextlib import redirect_stdout
from io import BytesIO, StringIO
import json
import os
from pathlib import Path
import re
import runpy
import socket
import sys
import tempfile
from unittest.mock import patch

import httpx
import openai
import streamlit as st
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "week11/week11_rag_integrated_revised"
APP = PACKAGE / "app.py"
TEMP = ROOT / "output/week11_integrated_checks"
TEMP.mkdir(parents=True, exist_ok=True)
(TEMP / ".gitignore").write_text("*\n", encoding="utf-8")
tempfile.tempdir = str(TEMP)
REAL_OPENAI = openai.OpenAI
for name in list(os.environ):
    if name.startswith("OPENAI_"):
        del os.environ[name]


def namespace(path=APP):
    """只載入函式與常數，不執行App畫面，也不載入.env。"""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    nodes = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))
             or (isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id.isupper())]
    ns = {"__file__": str(path)}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), ns)
    return ns


def expect_error(fn, *args):
    try:
        fn(*args)
    except (ValueError, UnicodeDecodeError):
        return
    raise AssertionError("預期失敗卻通過")


def check_build_and_shared():
    build = runpy.run_path(str(ROOT / "scripts/build_week11_integrated_rag_revised.py"))
    before = {p.relative_to(PACKAGE): p.read_bytes() for p in PACKAGE.rglob("*")
              if p.is_file() and "__pycache__" not in p.parts and not p.name.startswith(".env")}
    with redirect_stdout(StringIO()):
        build["main"]()
    assert all((PACKAGE / name).read_bytes() == data for name, data in before.items())
    assert APP.read_text(encoding="utf-8") == build["render_app"]()
    mine = {n.name: ast.dump(n) for n in ast.parse(APP.read_text(encoding="utf-8")).body if isinstance(n, ast.FunctionDef)}
    tracks = {
        "week09/week09_document_revised/teacher/app.py": ["extract_text", "clean_text", "chunk_text"],
        "week10/week10_semantic_search_revised/teacher/app.py": ["demo_vector", "cosine_similarity", "rank_chunks"],
        "week11/week11_rag_revised/teacher/app.py": ["split_chunks", "build_context", "build_input", "check_answer"],
    }
    for path, names in tracks.items():
        theirs = {n.name: ast.dump(n) for n in ast.parse((ROOT / path).read_text(encoding="utf-8")).body if isinstance(n, ast.FunctionDef)}
        for name in names:
            assert mine[name] == theirs[name], name
    for name in ("sample.txt", "sample.csv", "sample.pdf", "sample.docx"):
        assert (PACKAGE / "sample_data" / name).read_bytes() == (ROOT / "week09/sample_tata" / name).read_bytes()
    for path in [PACKAGE / "README.md", *ROOT.glob("week11/*整合RAG*修訂版.md")]:
        text = path.read_text(encoding="utf-8")
        assert "�" not in text and "???" not in text
        assert len(re.findall(r"^```", text, re.M)) % 2 == 0
        for link in re.findall(r"\]\(([^)]+)\)", text):
            if not link.startswith(("https://", "http://", "#")):
                assert (path.parent / link.split("#")[0]).exists(), (path, link)
    app_text = APP.read_text(encoding="utf-8")
    assert "raise NotImplementedError" not in app_text
    # 向量只列前5個數字：真實向量上千維，不整串印在頁面上
    assert '"vector": v}' not in app_text and '"vector": evidence["query_vector"]' not in app_text
    print("重建一致、三週10個共用函式AST、四範例原樣、向量只列前5個數字、完整App與講義連結通過")


def check_readers(ns):
    prepare = ns["prepare_document"]
    for name in ("sample.txt", "sample.csv", "sample.pdf", "sample.docx"):
        data = (PACKAGE / "sample_data" / name).read_bytes()
        doc = prepare(name, data, "utf-8-sig", 120, 20)
        assert doc["chunks"] and "地點" in doc["cleaned_text"]
        for item in doc["chunks"]:
            assert doc["cleaned_text"][item["start"]:item["end"]] == item["text"]
            assert item["source"] == name
    doc = prepare("sample.txt", (PACKAGE / "sample_data/sample.txt").read_bytes(), "utf-8-sig", 120, 20)
    assert len(doc["cleaned_text"]) == 121 and [(h["start"], h["end"]) for h in doc["chunks"]] == [(0, 120), (100, 121)]
    assert prepare("中文.md", "活動地點為圖書館".encode("cp950"), "cp950", 120, 20)["chunks"]
    # 空白行分段（App預設）：和第10、11週修訂版同一份3段文字、同樣的位置
    week11_doc = (ROOT / "week11/week11_rag_revised/sample_data/week09_cleaned_text.txt").read_text(encoding="utf-8").strip()
    for name in ("sample.txt", "sample.csv", "sample.pdf", "sample.docx"):
        doc = prepare(name, (PACKAGE / "sample_data" / name).read_bytes(), "utf-8-sig", 120, 20, True)
        assert doc["split"] == "空白行分段" and doc["chunk_size"] is None and doc["overlap"] is None
        for item in doc["chunks"]:
            assert doc["cleaned_text"][item["start"]:item["end"]] == item["text"] and item["source"] == name
    doc = prepare("sample.txt", (PACKAGE / "sample_data/sample.txt").read_bytes(), "utf-8-sig", 120, 20, True)
    assert doc["cleaned_text"] == week11_doc
    assert doc["chunks"] == namespace(ROOT / "week11/week11_rag_revised/teacher/app.py")["split_chunks"](week11_doc, "sample.txt")
    assert len(doc["chunks"]) == 3
    expect_error(prepare, "long.txt", ("長" * 1001).encode("utf-8"), "utf-8-sig", 120, 20, True)
    assert len(prepare("long.txt", ("長" * 1001).encode("utf-8"), "utf-8-sig", 1000, 0)["chunks"]) == 2
    for filename, data, enc, size, overlap in [
        ("empty.txt", b"", "utf-8-sig", 120, 20),
        ("blank.txt", b" \n\n", "utf-8-sig", 120, 20),
        ("large.txt", b"a" * (1024 * 1024 + 1), "utf-8-sig", 120, 20),
        ("long.txt", b"a" * 20001, "utf-8-sig", 120, 20),
        ("many.txt", b"a" * 10000, "utf-8-sig", 40, 20),
        ("bad.txt", b"\xff", "utf-8-sig", 120, 20),
        ("bad.txt", b"test", "utf-8-sig", 120, 120),
        ("bad.csv", b"x,x\n1,2", "utf-8-sig", 120, 20),
        ("bad.csv", b"x,y\n1", "utf-8-sig", 120, 20),
        ("bad.exe", b"abc", "utf-8-sig", 120, 20),
    ]:
        expect_error(prepare, filename, data, enc, size, overlap)
    from pypdf import PdfWriter
    pdf = PdfWriter()
    pdf.add_blank_page(width=200, height=200)
    raw = BytesIO()
    pdf.write(raw)
    expect_error(prepare, "scan.pdf", raw.getvalue(), "utf-8-sig", 120, 20)
    pdf.encrypt("offline-password")
    raw = BytesIO()
    pdf.write(raw)
    expect_error(prepare, "locked.pdf", raw.getvalue(), "utf-8-sig", 120, 20)
    print("實際TXT／MD／CSV／PDF／DOCX、cp950、兩種切塊（空白行分段＝第11週split_chunks、單段超過1000字元擋下）、"
          "來源切片、大小／空白／編碼／切塊／CSV／PDF邊界通過")


class Backend:
    """僅供教師測試：真實SDK連到記憶體HTTP後端，不存於教材App。"""
    def __init__(self, ns):
        self.ns, self.calls, self.settings = ns, [], []
        self.mode = "good"

    def handle(self, request):
        body = json.loads(request.content)
        path = request.url.path.removeprefix("/v1")
        self.calls.append((path, body))
        if self.mode == "429":
            return httpx.Response(429, json={"error": {"message": "offline-only", "type": "rate_limit_error"}})
        if self.mode == "timeout":
            raise httpx.ReadTimeout("offline-only", request=request)
        if path == "/embeddings":
            items = []
            for i, text in enumerate(body["input"]):
                v = self.ns["demo_vector"](text)
                v = v + [0.0 if any(v) else 1.0]
                if self.mode == "bad-vector":
                    v = [0.0] * 5
                items.append({"index": i, "object": "embedding", "embedding": v})
            if self.mode == "bad-index":
                items[0]["index"] = len(items)
            return httpx.Response(200, json={"object": "list", "model": body["model"], "data": list(reversed(items)),
                                             "usage": {"prompt_tokens": 1, "total_tokens": 1}})
        assert path == "/responses", path
        content = [{"type": "output_text", "text": "地點為圖書館討論室。[來源1]", "annotations": []}]
        if self.mode == "empty":
            content[0]["text"] = " "
        if self.mode == "refusal":
            content = [{"type": "refusal", "refusal": "offline-only"}]
        return httpx.Response(200, json={"id": "resp_test", "object": "response", "created_at": 0,
                                        "model": body["model"], "status": "incomplete" if self.mode == "incomplete" else "completed",
                                        "output": [{"id": "msg_test", "type": "message", "role": "assistant",
                                                    "status": "completed", "content": content}]})

    def client(self, **kwargs):
        self.settings.append({k: kwargs[k] for k in ("max_retries", "timeout")})
        return REAL_OPENAI(http_client=httpx.Client(transport=httpx.MockTransport(self.handle)), **kwargs)


def check_sdk(ns):
    backend = Backend(ns)
    with backend.client(api_key="offline-placeholder", max_retries=0, timeout=60.0) as client:
        vectors = ns["embed_texts_checked"](client, "embedding-test", ["地點圖書館", "報名截止"])
        assert vectors == [[2.0, 0.0, 0.0, 0.0, 0.0], [0.0, 2.0, 0.0, 0.0, 0.0]]
        for mode in ("bad-vector", "bad-index"):
            backend.mode = mode
            expect_error(ns["embed_texts_checked"], client, "embedding-test", ["地點"])
        backend.mode = "good"
        doc = ns["prepare_document"]("sample.txt", (PACKAGE / "sample_data/sample.txt").read_bytes(), "utf-8-sig", 120, 20)
        index = {"mode": "真實API", "model": "embedding-test", "vectors": vectors}
        evidence = ns["retrieve_evidence"](doc, index, "地點在哪裡？", vectors[0], 2, 0.2, 4000)
        assert len(evidence["ranking"]) == 2 and len(evidence["sources"]) == 1
        for mode in ("empty", "refusal", "incomplete"):
            backend.mode = mode
            expect_error(ns["generate_answer"], client, "answer-test", evidence)
        backend.mode = "good"
        answer = ns["generate_answer"](client, "answer-test", evidence)
        assert answer.endswith("[來源1]")
        payload = backend.calls[-1][1]
        assert payload["store"] is False and payload["instructions"] == ns["INSTRUCTIONS"]
        assert payload["input"] == evidence["input"]
        limited = ns["retrieve_evidence"](doc, index, "地點？", vectors[0], 2, 0.2, 5)
        before = len(backend.calls)
        assert ns["generate_answer"](client, "answer-test", limited) == ns["INSUFFICIENT"]
        assert not limited["sources"] and limited["hits"] and len(backend.calls) == before
        assert ns["check_answer"]("錯誤結論[來源1]", evidence["sources"])[0] == "有標來源：請回原文核對"
        assert ns["check_answer"]("地點[來源99]", evidence["sources"])[0].startswith("不合格")
    print("真實SDK＋MockTransport：回應index排序、壞向量／索引、送出預覽一致、store=False、拒答／未完成／空回答、無context零生成通過")


class Upload(BytesIO):
    def __init__(self, name, data):
        super().__init__(data)
        self.name = name


def check_readback(record):
    book = json.loads(next((ROOT / "week11").glob("*RAG文件問答*修訂版_學生版.ipynb")).read_text(encoding="utf-8"))
    code = "".join(next(c for c in book["cells"] if c["id"] == "w11r-download-run")["source"])
    with tempfile.TemporaryDirectory(dir=TEMP) as folder:
        old = Path.cwd()
        os.chdir(folder)
        try:
            path = Path("rag_record.json")
            path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
            with redirect_stdout(StringIO()) as printed:
                exec(code, {})
            assert "回查通過" in printed.getvalue()
            if record["context"]:
                changed = json.loads(json.dumps(record))
                changed["hits"][0]["text"] += "（竄改）"
                path.write_text(json.dumps(changed, ensure_ascii=False), encoding="utf-8")
                try:
                    exec(code, {})
                except AssertionError:
                    pass
                else:
                    raise AssertionError("竄改紀錄未被讀回格攔截")
        finally:
            os.chdir(old)


def check_app(ns):
    backend, downloads = Backend(ns), {}

    def download(label, data, file_name=None, **kwargs):
        if file_name and file_name.endswith(".json"):
            downloads[file_name] = json.loads(data)
        return False

    def click(at, key):
        downloads.clear()
        at.button(key=key).click().run()
        assert not at.exception, at.exception

    with patch.object(openai, "OpenAI", backend.client), patch("dotenv.load_dotenv"), \
            patch.object(st, "secrets", {}), patch.object(st, "download_button", download), \
            patch.dict(os.environ, {"OPENAI_API_KEY": "offline-placeholder"}):
        at = AppTest.from_file(str(APP), default_timeout=20).run()
        assert not at.exception and not backend.calls
        click(at, "prepare")
        assert len(at.session_state["document"]["chunks"]) == 3   # 預設空白行分段
        click(at, "embed_document")
        found = []
        for question in ("活動地點在哪裡？", "這場讀書交流辦在哪個空間？", "參加費用是多少？", "火星的平均氣溫是多少？"):
            at.text_input(key="question").set_value(question).run()
            click(at, "retrieve")
            found.append([h["chunk_id"] for h in at.session_state["evidence"]["sources"]])
        assert found == [[0], [], [2], []], found   # 與第10、11週修訂版離線結果相同
        at.text_input(key="question").set_value("活動地點在哪裡？").run()
        click(at, "retrieve")
        assert not backend.calls and at.session_state["evidence"]["sources"]
        check_readback(downloads["rag_record.json"])
        at.text_input(key="question").set_value("這場讀書交流辦在哪個空間？").run()
        assert at.session_state["evidence"] is None and at.session_state["query_cache"] is None
        click(at, "retrieve")
        assert at.session_state["evidence"]["ranking"] == []

        # 改用第9週固定字元：清掉舊文件；120／20把121字元切成2段
        at.radio(key="split").set_value("固定字元（第9週）").run()
        assert at.session_state["document"] is None and at.session_state["index"] is None
        click(at, "prepare")
        assert [(c["start"], c["end"]) for c in at.session_state["document"]["chunks"]] == [(0, 120), (100, 121)]
        at.radio(key="split").set_value("空白行分段（第10、11週）").run()
        click(at, "prepare")

        # 切模式只保留文件；文件Embedding一次，多題重用。
        at.checkbox(key="real_api").check().run()
        assert at.session_state["document"] and at.session_state["index"] is None
        click(at, "embed_document")
        assert [p for p, _ in backend.calls] == ["/embeddings"]
        at.text_input(key="question").set_value("活動地點在哪裡？").run()
        click(at, "retrieve")
        click(at, "answer")
        assert [p for p, _ in backend.calls] == ["/embeddings", "/embeddings", "/responses"]
        record = downloads["rag_record.json"]
        assert record["answer"] and "offline-placeholder" not in json.dumps(record)
        assert "vectors" not in json.dumps(record) and "query_vector" not in record
        check_readback(record)
        at.run()
        assert len(backend.calls) == 3  # 顯示與下載rerun不送出。
        at.slider(key="min_score").set_value(0.5).run()
        assert at.session_state["record"] is None and at.session_state["evidence"] is None
        click(at, "retrieve")
        assert len(backend.calls) == 3  # 同問題只重新排名。
        click(at, "answer")
        assert len(backend.calls) == 4
        at.text_input(key="question").set_value("火星的平均氣溫是多少？").run()
        click(at, "retrieve")
        before = len(backend.calls)
        click(at, "answer")
        assert len(backend.calls) == before and at.session_state["record"]["answer"] == ns["INSUFFICIENT"]
        check_readback(downloads["rag_record.json"])

        # 回答錯誤保留證據、清舊答案；未完成／拒答也不保存。
        at.text_input(key="question").set_value("活動地點在哪裡？").run()
        click(at, "retrieve")
        for mode in ("429", "timeout", "empty", "refusal", "incomplete"):
            backend.mode = mode
            before = len(backend.calls)
            click(at, "answer")
            assert at.error and at.session_state["record"] is None and at.session_state["evidence"]
            assert len(backend.calls) == before + 1, mode
        backend.mode = "good"
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            before = len(backend.calls)
            click(at, "answer")
            assert at.error and len(backend.calls) == before
        # 切塊變更清掉文件、向量與答案；建立失敗不留舊向量。
        at.slider(key="chunk_size").set_value(140).run()
        assert all(at.session_state[n] is None for n in ("document", "index", "record"))
        click(at, "prepare")
        backend.mode = "429"
        before = len(backend.calls)
        click(at, "embed_document")
        assert at.error and at.session_state["index"] is None and len(backend.calls) == before + 1
        backend.mode = "good"

        # 以替代上傳物件走真正reader與App流程，含同檔名內容更換。
        at.checkbox(key="real_api").uncheck().run()
        at.radio(key="source").set_value("上傳檔案").run()
        click(at, "prepare")
        assert at.error and at.session_state["document"] is None
        upload = Upload("自己的公告.md", "活動地點在圖書館討論室。".encode("utf-8"))
        with patch.object(st, "file_uploader", return_value=upload):
            at.run()
            click(at, "prepare")
            click(at, "embed_document")
            click(at, "retrieve")
            assert at.session_state["evidence"]["sources"][0]["source"] == upload.name
            assert len(at.session_state["document"]["chunks"]) == 1  # 單段無非法slider範圍。
            click(at, "clear")
            assert at.session_state["document"] is None
            click(at, "prepare")
        with patch.object(st, "file_uploader", return_value=Upload(upload.name, b"changed")):
            at.run()
            assert at.session_state["document"] is None
            click(at, "prepare")
            assert at.session_state["document"]["cleaned_text"] == "changed"
        with patch.object(st, "file_uploader", return_value=Upload("empty.txt", b"")):
            click(at, "prepare")
            assert at.error and at.session_state["document"] is None
        fresh = AppTest.from_file(str(APP), default_timeout=20).run()
        assert fresh.session_state["document"] is None and fresh.session_state["api_attempts"]["回答"] == 0
    assert all(s == {"max_retries": 0, "timeout": 60.0} for s in backend.settings)
    print("AppTest：預設0次、預設空白行分段離線4題[[0],[],[2],[]]、切換固定字元、分步結果、同文件多題、問題向量重用、無證據0生成、參數／模式／換檔／清除、"
          "同名新內容、上傳替身、單段、失敗清舊答案、429／逾時不重試、下載讀回與竄改攔截、session隔離通過")


def check_settings(ns):
    from streamlit.errors import StreamlitSecretNotFoundError

    class Missing:
        def get(self, *args):
            raise StreamlitSecretNotFoundError("offline-only")

    with patch.dict(os.environ, {"OPENAI_API_KEY": "from-env"}):
        with patch.object(st, "secrets", Missing()):
            assert ns["read_setting"]("OPENAI_API_KEY") == "from-env"
        with patch.object(st, "secrets", {"OPENAI_API_KEY": "from-cloud"}):
            assert ns["read_setting"]("OPENAI_API_KEY") == "from-cloud"
    assert 'load_dotenv(PACKAGE / ".env")' in APP.read_text(encoding="utf-8")
    assert (PACKAGE / ".env.example").is_file() and (PACKAGE / ".streamlit/secrets.example.toml").is_file()
    assert ".env" in (PACKAGE / ".gitignore").read_text(encoding="utf-8").splitlines()
    print("Secrets優先、無Secrets回退環境變數、.env載入位置與安全設定範本通過")


def main():
    # 即使未預期分支嘗試連外也立即失敗，不能落到真實API。
    with patch.object(socket.socket, "connect", side_effect=AssertionError("離線驗證禁止網路")), patch("dotenv.load_dotenv"):
        check_build_and_shared()
        ns = namespace()
        check_readers(ns)
        check_sdk(ns)
        check_settings(ns)
        check_app(ns)
    import importlib.metadata as md
    print("驗證環境：", sys.version.split()[0], {n: md.version(n) for n in ("streamlit", "openai", "pypdf", "python-docx", "python-dotenv", "httpx")})
    print("全部離線驗證通過；0次真實API。未測真實語意／回答品質、真人瀏覽器選檔、Colab、Cloud與試教。")


if __name__ == "__main__":
    main()
