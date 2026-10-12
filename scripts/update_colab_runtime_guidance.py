"""同步第5、6週150分鐘雙版的Colab提示；保留練習、ID與所有其他程式。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def runtime_guide(week):
    heading = "## 1️⃣ 環境與成本" if week == 5 else "## 1. 環境與執行方式"
    task_order = (
        "完成A→RUN_INPUT_CHECK→完成B→RUN_FAKE_STREAM_CHECK／RUN_OFFLINE_CHECKS"
        if week == 5 else "完成G→RUN_G_CHECK；完成A1/A2→RUN_A_SCHEMA_CHECK／RUN_A_LOCAL；B/C擇一先做本機檢查"
    )
    return f"""{heading}
金鑰只放Colab Secrets的`OPENAI_API_KEY`；本機用環境變數，不提交或顯示金鑰。
無金鑰可完成定義與離線練習。所有付費旗標預設False，安裝套件會連線但不呼叫模型。

**首次開啟／重啟後的順序**
1. 使用自己的Notebook副本，先儲存修改；確定所有`RUN_`旗標為False，互動CLI維持註解。
2. 新runtime或缺套件時執行`%pip`安裝格。已有符合需求的套件可跳過；若升級已匯入的套件，重新啟動工作階段，再從環境格開始。
3. 回查第3週「第二節：設定API Key」：確認Secrets名稱為`OPENAI_API_KEY`，允許目前Notebook的`Notebook access`，再重跑環境格。
4. 依序執行共用定義、練習定義與離線檢查：{task_order}。學生先補TODO；不用重寫已提供的helper或測試器。
5. 離線檢查通過後，只將當前付費活動旗標改True並執行該格；完成後恢復False，再儲存。勿保留True後使用「全部執行」。

runtime重啟後，程式編輯仍可從已儲存Notebook取得，但執行产生的變數、client與本機history／抽取結果須重新建立；未另存的執行狀態不會自動恢復。設定或變更Secrets後要重跑環境格，既有client不會自動更新。

**逾時、重試與版本紀錄**
下格用`API_TIMEOUT_SECONDS = 60.0`設定網路等待，並以`max_retries=0`關閉SDK自動重試。60秒是課堂起始設定，教師須依Colab實測調整；它控制網路各階段等待，不是整段串流或模型工作的總秒數上限。
每次API入口最多送出一次請求；手動重跑另計。逾時／失敗不代表免費，使用量與帳單仍須核對，先檢查錯誤再決定是否重跑。
環境格只顯示套件版本與金鑰是否可用。課前記錄Colab實測版本，再把安裝格改成驗證過的`套件==版本`；本次尚未在Colab驗證，保留現有升級方式，不把Windows完整快照當作Colab環境。
沿用`OPENAI_MODEL`與課程模型設定，課前確認教學帳號可用性。
""".replace("产生", "產生")


def change_setup(source, week):
    if "API_TIMEOUT_SECONDS" in source:
        return source
    source = source.replace("from openai import OpenAI", "import openai\nfrom openai import OpenAI", 1)
    if week == 6:
        source = source.replace("from pydantic import", "import pydantic\nfrom pydantic import", 1)
    old = "client = OpenAI() if" if week == 5 else "client = OpenAI(max_retries=0) if"
    assert source.count(old) == 1
    source = source.replace(old, (
        "# timeout控制網路等待，不是整段串流總時間；60秒為待課前實測的起始值。\n"
        "API_TIMEOUT_SECONDS = 60.0\n"
        "# 每次入口不自動重試，重跑需另計請求；缺金鑰保留離線模式。\n"
        "client = OpenAI(max_retries=0, timeout=API_TIMEOUT_SECONDS) if"
    ), 1)
    source += (
        '\n# 套件版本用於課前環境紀錄；第4週已教getattr的備援讀法。\n'
        'print("OpenAI SDK版本：", getattr(openai, "__version__", "版本資訊不可用"))\n'
    )
    if week == 6:
        source += 'print("Pydantic版本：", getattr(pydantic, "__version__", "版本資訊不可用"))\n'
    return source


def update(week):
    paths = sorted((ROOT / f"week{week:02d}").glob("*150分鐘修訂版_*.ipynb"))
    assert len(paths) == 2
    for path in paths:
        nb = json.loads(path.read_text(encoding="utf-8"))
        original = json.loads(json.dumps(nb))
        cells = nb["cells"]
        cells[4]["source"] = runtime_guide(week).splitlines(keepends=True)
        install = "".join(cells[5]["source"])
        if week == 5:
            install = install.replace("!pip install", "%pip install")
        if "目前kernel" not in install:
            install = "# %pip安裝至目前kernel；已安裝可跳過，升級已匯入套件後須重啟。\n" + install
        cells[5]["source"] = install.splitlines(keepends=True)
        cells[6]["source"] = change_setup("".join(cells[6]["source"]), week).splitlines(keepends=True)
        sources = cells[-1]
        source_text = "".join(sources["source"])
        if "https://developers.openai.com/api/reference/python" not in source_text:
            source_text += (
                "\n- [OpenAI官方Python SDK說明](https://developers.openai.com/api/reference/python)：timeout與max_retries。\n"
                "- [IPython %pip](https://ipython.readthedocs.io/en/stable/interactive/magics.html#magic-pip)：目前kernel的套件安裝。\n"
                "- [Colab FAQ](https://research.google.com/colaboratory/faq.html)：runtime與執行狀態。\n"
            )
        sources["source"] = source_text.splitlines(keepends=True)
        # 僅補銜接文字，不加入新的API活動或學生必做項目。
        bridge_cell = next(c for c in cells if c["cell_type"] == "markdown" and (
            ("完成檢核與後續銜接" in "".join(c["source"])) if week == 5 else c["id"] == "w06r-handoff"
        ))
        bridge = "".join(bridge_cell["source"])
        if "語音銜接（概念預告）" not in bridge:
            bridge += (
                "\n**語音銜接（概念預告）**：後續把已確認的辨識文字送進本週聊天函式；只有完整、可用的回答才交給TTS。文字delta顯示與音訊播放是不同步驟，本週不新增語音API。\n"
                if week == 5 else
                "\n**語音銜接（概念預告）**：後續可用本週Schema抽取已確認的逐字稿；格式通過仍要核對人名、日期、金額與原錄音。本週不新增錄音或語音API。\n"
            )
        bridge_cell["source"] = bridge.splitlines(keepends=True)
        assert [(c["id"], c["cell_type"]) for c in cells] == [(c["id"], c["cell_type"]) for c in original["cells"]]
        for index, (before, after) in enumerate(zip(original["cells"], cells)):
            if before["cell_type"] == "code" and index not in (5, 6):
                assert before == after, (path.name, before["id"])
        path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"已更新{path.name}，保留{len(cells)} cells。")


if __name__ == "__main__":
    for week in (5, 6):
        update(week)
