"""無網路檢查Colab修訂、假SDK設定及逾時分流；不安裝套件或讀取真實金鑰。"""
import ast
import contextlib
import copy
import io
import json
import os
import re
import subprocess
import sys
import types
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def run_offline(path):
    nb = json.loads(path.read_text(encoding="utf-8"))
    before = json.loads(subprocess.run(
        ["git", "show", f"HEAD:{path.relative_to(ROOT).as_posix()}"],
        cwd=ROOT, check=True, capture_output=True,
    ).stdout.decode("utf-8"))
    assert [(c["id"], c["cell_type"]) for c in nb["cells"]] == [(c["id"], c["cell_type"]) for c in before["cells"]]
    ids = [c["id"] for c in nb["cells"]]
    assert len(ids) == len(set(ids))
    changed_code = []
    ordinary = 0
    for index, (new, old) in enumerate(zip(nb["cells"], before["cells"])):
        source = "".join(new["source"])
        assert '**語音' not in source
        assert not re.search(r"\?{4,}|\ufffd|sk-[A-Za-z0-9_-]{20,}", source)
        if new["cell_type"] != "code":
            continue
        assert new["outputs"] == [] and new["execution_count"] is None
        if new != old:
            changed_code.append(index)
        if index == 5:
            assert "%pip install" in source and "!pip install" not in source
            continue
        ast.parse(source)
        ordinary += 1
    # 只有安裝／環境格可修改程式；所有學生答案與正式練習維持原樣。
    assert set(changed_code) <= {5, 6}, changed_code
    assert nb["metadata"] == before["metadata"]
    constructors = []
    sdk = types.ModuleType("openai")
    sdk.__version__ = "offline-fixture"

    def constructor(**kwargs):
        constructors.append(kwargs)
        return types.SimpleNamespace(responses=types.SimpleNamespace())

    sdk.OpenAI = constructor
    colab = types.ModuleType("google.colab")
    colab.userdata = types.SimpleNamespace(get=lambda name: "")
    env = {"__name__": "__main__"}
    with patch.dict(sys.modules, {"openai": sdk, "google.colab": colab}), patch.dict(os.environ, {"OPENAI_API_KEY": ""}), contextlib.redirect_stdout(io.StringIO()):
        for index, cell in enumerate(nb["cells"]):
            if cell["cell_type"] == "code" and index != 5:
                exec(compile("".join(cell["source"]), cell["id"], "exec"), env)
        assert env["client"] is None and not constructors
        assert all(value is False for name, value in env.items() if name.startswith("RUN_"))

        # 設定假金鑰時只記錄建構參數，沒有網路client或真實秘密。
        colab.userdata = types.SimpleNamespace(get=lambda name: "offline-placeholder")
        setup_env = {}
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            exec("".join(nb["cells"][6]["source"]), setup_env)
        assert constructors == [{"max_retries": 0, "timeout": 60.0}]
        assert setup_env["API_TIMEOUT_SECONDS"] == 60.0
        assert "offline-placeholder" not in capture.getvalue()
        assert "offline-fixture" in capture.getvalue()

        # Secrets無權限且無環境金鑰，仍能進入離線模式。
        constructors.clear()
        os.environ["OPENAI_API_KEY"] = ""

        def denied(name):
            raise PermissionError("fixture: access denied")

        colab.userdata = types.SimpleNamespace(get=denied)
        denied_env = {}
        exec("".join(nb["cells"][6]["source"]), denied_env)
        assert denied_env["client"] is None and not constructors

    return nb, env, ordinary


def check_timeout(env, week):
    calls = []

    def timeout(**kwargs):
        calls.append(kwargs)
        raise TimeoutError("離線模擬網路逾時")

    fake = types.SimpleNamespace(responses=types.SimpleNamespace(create=timeout))
    if week == 5:
        for name in ("ask_chat_once", "ask_chat_stream"):
            state = env["new_chat_state"]()
            snapshot = copy.deepcopy(state)
            prior_count = len(calls)
            try:
                env[name](state, "測試問題", api_client=fake)
            except RuntimeError:
                pass
            else:
                raise AssertionError("逾時不應回傳成功")
            assert state == snapshot and len(calls) == prior_count + 1
    else:
        ok, result = env["extract_structured_safe"]("測試文字", env["event_schema"], "timeout_fixture", api_client=fake)
        assert ok is False and isinstance(result, str) and "TimeoutError" in result
        assert len(calls) == 1
    return len(calls)


def check_builder(notebooks):
    import build_week06_revision
    captured = {}

    def save(path, text, **kwargs):
        captured[path.name] = json.loads(text)
        return len(text)

    # 重建只攔截輸出，確保後續重建不會撤銷本次Colab修訂。
    with patch.object(Path, "write_text", save):
        build_week06_revision.build(False)
        build_week06_revision.build(True)
    for path, nb in notebooks:
        built = captured[path.name]
        assert [(c["id"], c["cell_type"]) for c in built["cells"]] == [(c["id"], c["cell_type"]) for c in nb["cells"]]
        for new, old in zip(built["cells"], nb["cells"]):
            assert "".join(new["source"]).strip() == "".join(old["source"]).strip(), new["id"]


def main():
    summaries = []
    sixth = []
    for week in (5, 6):
        for path in sorted((ROOT / f"week{week:02d}").glob("*150分鐘修訂版_*.ipynb")):
            nb, env, ordinary = run_offline(path)
            teacher = path.name.endswith("教師版.ipynb")
            timeout_count = 0
            if teacher:
                timeout_count = check_timeout(env, week)
                if week == 5:
                    with contextlib.redirect_stdout(io.StringIO()):
                        assert len(env["run_offline_checks"]()) == 5
            if week == 6:
                sixth.append((path, nb))
            summaries.append({"week": week, "edition": "教師" if teacher else "學生", "cells": len(nb["cells"]), "python": ordinary, "fake_timeout_calls": timeout_count})
    check_builder(sixth)
    print(json.dumps({"status": "passed", "notebooks": summaries, "constructor_options": {"max_retries": 0, "timeout": 60.0}, "week06_rebuild": "matched", "real_api_calls": 0}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
