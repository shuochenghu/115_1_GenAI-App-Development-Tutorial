"""重建第14週學生／教師Notebook、閱讀稿、單檔App及離線資料；0次API。

核心來源：scripts/templates/week14_agent_core.py；文字與配套由本檔生成。
不覆蓋手寫README、教師導讀、B表、工具規格或真實.env／Secrets。
"""
import ast
import json
from pathlib import Path
import re
from textwrap import dedent

from notebook_cell_notes import annotate_dependencies

ROOT = Path(__file__).resolve().parents[1]
WEEK = ROOT / "week14"
PACKAGE = WEEK / "week14_agent"
TITLE = "生成式AI應用開發_第14週_Agent基礎與工作流程"
PREFIX = "w14-"
REQUIREMENTS = "streamlit==1.60.0\nopenai==2.49.0\npython-dotenv==1.2.2\nhttpx==0.28.1\nbeautifulsoup4==4.14.3\n"
CORE = dict(re.findall(r"^# %% (\w+)\n(.*?)(?=^# %% |\Z)",
    (ROOT / "scripts/templates/week14_agent_core.py").read_text(encoding="utf-8"), re.M | re.S))
CORE = {name: source.strip() + "\n" for name, source in CORE.items()}
STUDENT_A = CORE["a"][:CORE["a"].index("    # 教師完成參考")]+'''    # TODO A：依規格決定停止代號，或回傳None放行。
    # 請先判斷次數是否已滿，再判斷是否重複；保留上面的型別檢查。
    raise NotImplementedError("請完成TODO A：停止規則，修改後重跑定義格")
'''
OFFLINE = {
    "正常": [
        {"步驟": 1, "動作": "搜尋", "參數": "Streamlit forms submit rerun", "觀察": "手寫示意：有候選s1，尚未閱讀原文", "下一步": "讀s1"},
        {"步驟": 2, "動作": "閱讀", "參數": "s1", "觀察": "手寫示意：原文片段有表單提交條件", "下一步": "整理有來源的答案"},
        {"步驟": 3, "動作": "回答", "參數": "來源s1", "觀察": "手寫示意：核對提交條件後回答", "下一步": "停止"}],
    "不足與重查": [
        {"步驟": 1, "動作": "搜尋", "參數": "classroom next week", "觀察": "手寫示意：沒有合格候選", "下一步": "換一次關鍵字"},
        {"步驟": 2, "動作": "搜尋", "參數": "course classroom schedule", "觀察": "手寫示意：官方文件仍無法支持本班資訊", "下一步": "說明不足"},
        {"步驟": 3, "動作": "回答", "參數": "insufficient", "觀察": "手寫示意：沒有本班教室證據，不杜撰", "下一步": "停止"}],
    "重複": [
        {"步驟": 1, "動作": "搜尋", "參數": "forms submit", "觀察": "手寫示意：已執行一次", "下一步": "再提相同字詞"},
        {"步驟": 2, "動作": "執行前阻擋", "參數": "forms submit", "觀察": "repeated_action；工具不再加一次", "下一步": "停止"}],
    "達上限": [
        {"步驟": 1, "動作": "搜尋", "參數": "forms", "觀察": "手寫示意：工具1／3", "下一步": "閱讀"},
        {"步驟": 2, "動作": "閱讀", "參數": "s1", "觀察": "手寫示意：工具2／3", "下一步": "閱讀另一頁"},
        {"步驟": 3, "動作": "閱讀", "參數": "s2", "觀察": "手寫示意：工具3／3", "下一步": "下一輪關閉工具"},
        {"步驟": 4, "動作": "回答或說明不足", "參數": "tool_choice=none", "觀察": "手寫示意：只用已有觀察，不執行第4個工具", "下一步": "停止"}],
}
HTML = """<!doctype html><html lang="zh-TW"><body><nav>選單</nav><main>
<h1>手寫HTML抽取示意</h1><p>示意資料：表單內容在提交時送出。這不是下載的官方網頁。</p>
<script>這段不應放入本文</script></main><footer>頁尾</footer></body></html>"""
CELL_NOUNS = {
    "install": "安裝格", "secrets": "金鑰設定格", "imports": "匯入格", "policy": "規格格",
    "offline": "離線紀錄格", "task": "搜尋規格格", "task-demo": "搜尋規格示範格",
    "html-demo": "HTML短例格", "reader": "閱讀工具格", "protocol": "工具來回示意格",
    "a": "A定義格", "a_check": "A檢查函式格", "a-run": "A執行格",
    "response": "回應檢查格", "search": "搜尋工具格", "record": "紀錄函式格",
    "loop-demo": "有限迴圈短例格", "runner": "Agent函式格", "live": "真實執行格",
    "save": "教師保存格", "download": "下載讀回格", "syntax": "語法短例格",
}


def text_block(text):
    return dedent(text).strip() + "\n"


def cells_for(teacher):
    cells = []

    def md(tag, text):
        cells.append({"cell_type": "markdown", "id": PREFIX+tag, "metadata": {},
                      "source": text_block(text).splitlines(keepends=True)})

    def code(tag, source, requests=0):
        source = f"# 用途：{CELL_NOUNS[tag]}；先備：無；最多{requests}次API\n" + source.strip() + "\n"
        cells.append({"cell_type": "code", "id": PREFIX+tag,
                      "metadata": {"teaching": {"requires": [], "api_requests_max": requests}},
                      "source": source.splitlines(keepends=True), "outputs": [], "execution_count": None})

    md("cover", f'''
        # 第14週｜Agent基礎與工作流程・{'教師版' if teacher else '學生版'}

        本週要做一個會選工具、會看結果、也會停下來的官方文件查核助手。
        第13週固定「準備搜尋→搜尋回答」，本週由單一模型選擇搜尋、閱讀或回答；程式掌握權限與上限。
        <font color="#C62828"><b>預設0次API。離線手寫情境不是模型或網路搜尋成果。</b></font>

        先備：第2、3、5、6、7、13週的函式、JSON、Responses、對話歷史、Schema、表單與工具回傳。
        唯一程式練習為A停止規則；B是路徑與原文查核。{'教師版提供A答案及B判讀。' if teacher else '請保留並完成TODO，不用重寫工具後端。'}

        | 分鐘 | 活動 |
        |---:|---|
        | 15 | 情境與第13週對照 |
        | 20 | 手寫工具往返與離線紀錄 |
        | 20 | 搜尋與閱讀工具 |
        | 25 | A停止規則 |
        | 25 | 有限迴圈與真實示範 |
        | 30 | App、B與下載讀回 |
        | 15 | 錯誤、作業及第15週 |

        核心150分鐘，另留休息10分鐘與排障20分鐘。完成後應能說明：誰選下一步、誰執行、根據什麼停止，以及答案的原文證據在哪裡。
    ''')
    md("environment", '''
        ## 1 環境與請求額度

        Notebook可在Colab逐格執行；App要在VS Code本機執行，不在Colab啟動網頁服務。
        先用第3節手寫情境理解流程，再做A；第9節才需要金鑰。
        本週固定依賴：openai 2.49.0、httpx 0.28.1、beautifulsoup4 4.14.3；本機App另需Streamlit 1.60.0、python-dotenv 1.2.2。
        以下安裝格預設關閉。Colab需要時改True執行一次；若提示重啟工作階段，重啟後改回False，從設定及匯入格依序重跑。

        每題最多4次外層決策＋2次搜尋後端＝6次Responses、2次內建搜尋及2次一般網頁HTTP。
        工具總數只有3次，因此不是搜尋2次再閱讀2次都能用滿。兩題最多12次Responses；額外重跑另計。
        格首「先備／用到前面名稱」表示執行順序；修改A後務必重跑A定義與檢查格。
    ''')
    code("install", text_block('''
        import subprocess
        import sys

        RUN_INSTALL = False
        if RUN_INSTALL:
            subprocess.check_call([sys.executable, "-m", "pip", "install",
                                   "openai==2.49.0", "httpx==0.28.1", "beautifulsoup4==4.14.3"])
        else:
            print("未安裝套件；需要時才開啟RUN_INSTALL，0次API")
    '''))
    md("keys-note", '''
        ### 1-1 金鑰與模型設定

        Colab左側Secrets新增OPENAI_API_KEY並授權本Notebook；本機可在啟動前設環境變數，App也可讀自己的.env。
        以下預設不讀Secrets、不顯示金鑰。要跑第9節時才開啟；授權或重啟後重跑本格。
        模型預設gpt-5.4-mini，可用OPENAI_MODEL覆蓋；帳號權限及模型組合仍需課前實測。
    ''')
    code("secrets", text_block('''
        import os
        from importlib.metadata import version

        LOAD_COLAB_SECRETS = False
        if LOAD_COLAB_SECRETS:
            from google.colab import userdata
            os.environ["OPENAI_API_KEY"] = userdata.get("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
        print("模型：", model)
        print("套件版本：", {name: version(name) for name in ("openai", "httpx", "beautifulsoup4")})
        print("本格0次API；不顯示金鑰")
    '''))
    md("concept", '''
        ## 2 找到資料後，接下來做什麼

        問題：「在Streamlit表單裡，修改輸入值和按下提交，分別何時重新執行？」
        如果第一次搜尋只找到表單元件清單，你會換關鍵字、打開原文，還是先說證據不足？
        這個「看結果，再決定下一步」就是本週要觀察的Agent工作流程。

        | 名詞 | 在本週看什麼 |
        |---|---|
        | planning | 下一次選的工具及參數；不要求隱藏推理過程 |
        | tool use | 模型提出呼叫後，Python實際執行工具 |
        | observation | 工具回傳候選來源、原文或明確錯誤 |
        | final answer | 整理已讀證據，或說明不足與限制 |
        | stop | 程式擋住重複或超額，模型也可提早回答 |

        第13週的步驟由程式固定；本週允許模型選下一步，但它不能提高額度、改範圍或執行任意程式。
    ''')
    md("trace-note", '''
        ## 3 先看離線紀錄

        以下全是手寫情境，沒有發請求，也不代表模型一定走相同路徑。修改case可比較正常、重查、重複及達上限。
        先找出「觀察」和「下一步」的關係，再數工具；最後回答也占一輪模型，但不占工具次數。
    ''')
    code("offline", "offline_traces = " + repr(OFFLINE) + '\ncase = "正常"\nfor step in offline_traces[case]:\n    print(step)\nprint("手寫示意：本格實際API 0次、HTTP 0次")')
    md("trace-observe", '''
        ### 3-1 讀完紀錄後回答

        正常示意有3個模型步驟、2個工具動作；不足示意可換一次搜尋字詞後停止。
        重複示意的第二次提案沒有執行，因此不增加工具次數；達上限示意的最後一輪只整理已有資料。
        請記下：哪一步看到新資料？如果閱讀失敗，應說「讀不到」還是「官方沒有寫」？後者需要更多證據。
    ''')
    md("tools-note", '''
        ## 4 兩個工具與資料分工

        | 元件 | 輸入 | 輸出 | 誰執行 |
        |---|---|---|---|
        | search_official | search_query、scope | 搜尋摘要、候選source_id與網址 | Python送一次搜尋後端API |
        | read_official_page | 已登記source_id | 抽取的網頁原文片段或錯誤 | Python送一次HTTP |
        | 最後答案 | 已有工具觀察 | status、answer、source_ids | 外層模型，再由程式驗證 |

        搜尋摘要是模型整理的線索；閱讀片段才是App抓取並抽取的網頁文字。兩者不能混稱原文。
        下方先匯入套件及定義規格，不會呼叫API。對照上學期Skill：用途對應description、規則對應INSTRUCTIONS、輸入對應Schema、腳本對應Python函式；文件不會被API自動載入。
    ''')
    code("imports", CORE["imports"])
    code("policy", CORE["policy"])
    md("contract-note", '''
        ### 4-1 沿用第13週搜尋規格

        `build_search_task(search_query, scope)`先檢查1～80字元關鍵字與範圍，回傳query及allowed_domains；本身0次API。
        例如`build_search_task("forms submit", "Streamlit")`中，第一個值是關鍵字，第二個是使用者範圍。
        本週`official_url(url, scope)`只接受精確官方主機與HTTPS；保留可能決定內容的query，只去掉頁內錨點。
    ''')
    code("task", CORE["task"])
    code("task-demo", 'task_demo = build_search_task("forms submit", "Streamlit")\nprint(task_demo)\nprint(official_url("https://docs.streamlit.io/develop/concepts/architecture/forms?view=full#submit", "Streamlit"))')
    md("html-note", '''
        ### 4-2 從HTML看到本文

        網頁包含選單、頁尾及script。先用一份手寫HTML短例，留下main內的文字；這只是本機抽取，不是下載官方頁面。
        BeautifulSoup的第一個參數是HTML資料，第二個`html.parser`是Python內建解析方式；`select`找指定標籤，`decompose`移除；`get_text`以換行連接文字並去掉邊緣空白。
        正式`read_official_page`沿用同方法，先選article／main等本文區，再節錄最多6000字元。
    ''')
    code("html-demo", 'html_demo = ' + repr(HTML) + '\nsoup_demo = BeautifulSoup(html_demo, "html.parser")\nfor element in soup_demo.select("script,style,nav,header,footer,aside,noscript"):\n    element.decompose()\nprint(soup_demo.find("main").get_text("\\n", strip=True))')
    md("reader-note", '''
        ### 4-3 完整提供的閱讀工具

        `read_official_page(source_id, scope, sources)`接收候選代號、本次範圍及本任務來源dict，成功回ok、excerpt、sha256與truncated，失敗回ok=False及error。
        只讀已登記官方HTML；最多1MB、10秒網路等待、不跟轉址、不執行JavaScript。httpx.stream逐批讀bytes，超限立即停止；10秒不是整個任務總時間。
        定義下方函式不連網；第9節或App真實提交後才使用。無需完成新的TODO。
    ''')
    code("reader", CORE["reader"])
    md("protocol-note", '''
        ## 5 一次工具往返如何接下一輪

        模型輸出name、arguments與call_id。arguments是JSON字串，要解析成dict；工具結果也用同一call_id送回。
        以下手寫提案與觀察是離線示意，和A是否完成無關。

        ```mermaid
        flowchart LR
            M[模型選工具] --> V[程式驗提案與額度]
            V --> T[白名單工具執行]
            T --> O[同call_id回傳觀察]
            O --> N[模型再選下一步或回答]
        ```
    ''')
    code("protocol", text_block('''
        import json as protocol_json

        demo_call = {"type": "function_call", "name": "read_official_page",
                     "call_id": "call_demo_1", "arguments": '{"source_id": "s1"}'}
        demo_observation = {"ok": False, "source_id": "s1", "error": "手寫示意：頁面需要轉址"}
        demo_followup = [{"role": "user", "content": "手寫示意：讀取已登記s1"},
                         demo_call, {"type": "function_call_output", "call_id": demo_call["call_id"],
                         "output": protocol_json.dumps(demo_observation, ensure_ascii=False)}]
        print("參數型別：", type(demo_call["arguments"]).__name__)
        print(protocol_json.dumps(demo_followup, ensure_ascii=False, indent=2))
    '''))
    md("a-note", '''
        ## 6 A：什麼時候不能再執行工具

        先跑第3節離線紀錄，再修改下方A。這是唯一程式TODO；不是要寫整個Agent。

        | 項目 | 規格 |
        |---|---|
        | tool_count | 已執行的工具次數，非負int，失敗也算 |
        | max_tools | 正int，主線傳3；改成1會更早停止 |
        | is_repeat | 程式已算好的bool，相同工具與正規化參數曾出現 |
        | return | 次數已滿→tool_limit；否則重複→repeated_action；其餘→None |
        | 同時成立 | 次數上限優先 |

        保留型別檢查，完成判斷後重跑定義格，再跑第7節。必須return，不能只print。
        觀察紀錄存a_checks；完整迴圈把本次回傳存reason。下游程式、動作正規化與工具分派都已提供，不需改。
    ''')
    code("a", CORE["a"] if teacher else STUDENT_A)
    md("a-check-note", '''
        ## 7 A自我檢查與失敗回查

        先執行或重跑第6節A定義格，再依序跑以下兩格。check_a提供固定資料，回傳7筆檢查紀錄；不要修改它來讓錯誤答案通過。
        A未完成只顯示提示，a_checks保持None，不影響前面的完整示範。若收到判斷錯誤，對照規格檢查≥邊界、優先順序及return。
    ''')
    code("a_check", CORE["a_check"])
    code("a-run", text_block('''
        a_checks = None
        try:
            a_checks = check_a()
            print("A自我檢查通過：", len(a_checks), "筆；0次API")
            print(a_checks)
        except NotImplementedError:
            print("請完成A後重跑A定義格與本格；尚未通過，不會呼叫API")
    '''))
    md("a-observe", '''
        ### 7-1 檢查通過代表什麼

        七筆涵蓋正常放行、剛好等於上限、超過上限、重複、兩條件同時成立及改上限。
        通過只表示這組規則符合規格，不證明模型會選對工具或答案正確。
        看看2／3次放行與3／3次停止有何差別：已用滿時，下一個提案尚未執行，不能先花錢再檢查。
    ''')
    md("loop-note", '''
        ## 8 把一次來回放進有限迴圈

        先用下方短例看懂：最多4輪，最後一輪關閉工具。實際模型也可以提早回答，不需要用滿。
        `range(1, 5)`產生1、2、3、4；break離開迴圈，並不會替你呼叫工具。第2週已學的list、dict、JSON及例外處理沿用於正式程式。
    ''')
    code("loop-demo", text_block('''
        # 手寫動作清單只用來展示迴圈控制，沒有假裝呼叫模型。
        planned_steps = ["搜尋", "閱讀", "閱讀", "回答"]
        for turn in range(1, 5):
            allow_tools_demo = turn < 4
            print("輪次：", turn, "允許工具：", allow_tools_demo, "手寫動作：", planned_steps[turn - 1])
            if planned_steps[turn - 1] == "回答":
                break
        print("實際API 0次")
    '''))
    md("response-note", '''
        ### 8-1 回應先檢查，才執行

        下方三個檢查函式完整提供，都是0次API。先找責任，不必重寫解析器。

        | 函式 | 參數與回傳 |
        |---|---|
        | check_response(response) | SDK物件；拒答或未完成丟出停止代號 |
        | read_function_call(response, scope, sources) | 本輪回應、使用者範圍、任務來源dict；回(call, arguments)，沒提工具則(None, None) |
        | check_final(data, sources) | 最後答案dict與來源dict；回驗證過的data |

        函式提案最多一個，scope不能換，閱讀只能用已登記來源；call_id不得重複。
        最後答案三欄status、answer、source_ids：answered至少引用一個成功閱讀來源；insufficient說明缺什麼，仍不代表官方一定沒有資料。
    ''')
    code("response", CORE["response"])
    md("search-note", '''
        ### 8-2 搜尋後端是額外一次請求

        `search_official(client, search_query, scope, record)`接收已設定的SDK client、關鍵字、範圍及任務紀錄dict。
        record提供model，並保存requests、sources與當前工具trace；函式回搜尋摘要及候選清單。每次呼叫最多1次Responses＋1次內建工具。
        `tools`指定web_search與allowed_domains，`tool_choice`強制這個後端搜尋，`max_tool_calls=1`限制內建工具，`include`要求查閱來源。
        `max_output_tokens=1800`限制輸出token，`store=False`不儲存這次回應供ID續接，但問題仍會傳送到API。
        和第13週相同，查詢UTC時間不能代替網頁發布日期；沒有候選可回空清單，不能補造網址。
    ''')
    code("search", CORE["search"])
    md("record-note", '''
        ### 8-3 先記嘗試，才開始請求

        `new_record(question, scope, model)`建立本次dict；`record_counts(record)`從工具trace及請求requests重算次數。
        外層一次決策是一次Responses；search_official還會增加一次搜尋後端Responses；read_official_page只加HTTP。
        usage拿不到時保留None，不能寫成零費用。成功與失敗都記錄，不把逾時當沒有請求。
    ''')
    code("record", CORE["record"])
    md("runner-note", '''
        ### 8-4 完整Agent：沿著四個區塊閱讀

        `run_agent(client, question, scope, model)`回傳本次紀錄dict；A未完成或輸入不合格時，任何請求前就停止。
        依序看：預檢→外層for與請求→提案／停止／執行→回傳觀察。來源與HTTP解析已在前面函式，不需追另一個專案檔。
        外層`tool_choice="auto"`讓模型選；`parallel_tool_calls=False`至多一個函式；最後輪次改none。text.format沿用第6週規格，只約束最後文字答案。
        每輪帶回整份output（包含可能的reasoning）及同call_id結果；畫面只顯示工具與觀察，不顯示隱藏推理。
        history.extend把output逐項加到歷史，append則加入一筆function_call_output；兩者都保留原使用者輸入。
        A的reason在工具執行前判斷；SDK的max_retries=0表示傳輸不重試。換關鍵字再搜尋是另一個有計數的工具步驟。
    ''')
    code("runner", CORE["runner"])
    md("live-note", '''
        ## 9 真實API：先確認A，再開啟本格

        先完成環境、金鑰設定及第4～8節定義。確認A檢查通過後，在本格改RUN_AGENT=True，執行一次。
        問題與範圍就在本格；每次重跑最多6次Responses＋2次內建搜尋＋2次HTTP，額外重跑另計。
        `OpenAI(api_key=..., max_retries=0, timeout=60)`中的key來自環境，停用自動重試，60秒是網路等待設定，不是整個任務總時間。
        本格每次先清record；完成答案、不足與服務失敗分開呈現。遇到錯誤先記錄，避免不斷重跑。
    ''')
    code("live", text_block('''
        import os
        from openai import OpenAI

        RUN_AGENT = False
        agent_record = None
        question = "在Streamlit表單裡，修改輸入值和按下提交按鈕，分別何時讓程式重新執行？請找官方依據。"
        scope = "Streamlit"
        if RUN_AGENT:
            try:
                check_a()
                api_key = os.getenv("OPENAI_API_KEY", "").strip()
                if not api_key:
                    raise ValueError("缺少OPENAI_API_KEY；先完成環境或Colab Secrets設定")
                with OpenAI(api_key=api_key, max_retries=0, timeout=60) as client:
                    agent_record = run_agent(client, question, scope, model)
                print("停止原因：", STOP_LABELS[agent_record["stop_reason"]])
                print("次數：", agent_record["counts"])
                print("答案：", agent_record["final"])
                for event in agent_record["trace"]:
                    print(event)
            except (NotImplementedError, AssertionError, ValueError):
                print("尚未開始：請確認A與自我檢查、問題及Secrets設定；未送出請求")
        else:
            print("RUN_AGENT=False：0次API；不產生假答案")
    '''), 6)
    md("save-note", '''
        ### 9-1 選用：教師保存本次紀錄

        只有第9節本次真的產生agent_record才可保存；失敗紀錄也如實保存。預設關閉，0次新增API。
        檔案是課堂證據，不含金鑰或reasoning；仍要檢查是否含不應公開的問題。App可直接下載，不需要用這格。
    ''')
    code("save", text_block('''
        import json
        from pathlib import Path

        SAVE_TEACHER_RECORD = False
        if SAVE_TEACHER_RECORD and agent_record is not None:
            Path("agent_record.json").write_text(json.dumps(agent_record, ensure_ascii=False, indent=2), encoding="utf-8")
            print("已保存本次agent_record.json；0次新增API")
        else:
            print("本格未保存；未啟用或本次尚無紀錄")
    '''))
    md("b-note", '''
        ## 10 B：從工具路徑回查原文

        請保留正常與不足兩筆真實執行（失敗也照實記錄）。課堂紀錄可沿用，不為湊步數重跑。
        使用[B紀錄表](week14_agent/觀察與查核紀錄.md)，填問題、範圍、模式、模型、時間、各步參數與觀察、停止原因及實際計數。
        選一個答案主張→找source_id→看sources中的excerpt→打開該網址→核對原文是否支持；再核對一個版本／數字／日期。
        沒有網頁日期就填未標示；抓取UTC時間只是我們何時讀取。
        錯誤或邊界可用離線固定情境，不刻意耗費API製造故障。格式／引用通過不代表語意正確。
    ''' + ('''

        教師判讀示意（虛構，非API成果）：學生說「找到表單文件」還不夠；須寫出主張、來源代號、對應短句及適用條件。
        若工具回讀取失敗，合格說法是「這次沒有取得可用本文」；不能推論「官方沒有說」。如果實際路徑沒有重查，寫沒有重查即可。
    ''' if teacher else ""))
    md("app-note", '''
        ## 11 把同一個A移入App

        開啟[App README](week14_agent/README.md)。只把完成的stop_reason移入student/app.py對應位置，其他核心已和Notebook同步，不再寫另一套Agent。
        在week14/week14_agent資料夾建立或使用獨立環境，安裝requirements，再執行`python -m streamlit run student/app.py`。
        先選離線情境並按執行檢查A；再設定.env、開API、選範圍並提交問題。離線情境只重播手寫步驟，不下載成真實紀錄。
        真實提交會跑完有限任務，再依序展示各步觀察、最後狀態及次數。下載agent_record.json後做11-1。
        新題先清舊答案；切範圍／模式或失敗不沿用前次成功。一般rerun、展開與下載不重新請求。
    ''')
    md("download-note", '''
        ### 11-1 下載後重新讀回

        把App的agent_record.json放到Notebook工作資料夾；Colab拖進左側「檔案」。這格自帶必要程式，0次API，不需要先跑前面格子。
        第二份檔名可能叫agent_record (1).json，改下面path後重跑。沒有檔案只提示，不使用示意檔冒充驗證。
        檢查call_id、來源順序、閱讀片段雜湊、引用、次數與停止後事件；通過只表示紀錄一致，不能證明真實連線、真人操作或答案正確。最後仍要填B。
        完整檢查函式直接提供，不必逐行重寫；若AssertionError，依中文訊息回查該份紀錄。
    ''')
    code("download", CORE["download_check"] + text_block('''
        import json
        from pathlib import Path

        path = Path("agent_record.json")
        downloaded_record = None
        if path.is_file():
            downloaded_record = json.loads(path.read_text(encoding="utf-8"))
            print("紀錄一致性檢查通過：", check_record(downloaded_record))
            print("最後狀態：", downloaded_record["run_status"], "；請繼續人工回查來源")
        else:
            print("尚無agent_record.json；先從App下載並放到目前資料夾，再重跑。0次API")
    '''))
    md("syntax-note", '''
        ## 12 常見錯誤與必要語法回查

        | 現象 | 回查 |
        |---|---|
        | 改完A還提示未完成 | 重跑第6節定義，再第7節；App要儲存student/app.py |
        | 缺金鑰或Secrets未授權 | 第1-1節；不把金鑰貼到程式或輸出 |
        | invalid_call | 看工具名稱、scope、來源代號與唯一call_id |
        | invalid_final | answered是否引用成功閱讀的來源；是否真有三欄 |
        | 讀取轉址或無本文 | 本週不跟轉址、不跑JavaScript；改題或列限制，不擴充任意爬取 |
        | 答案與原文不符 | 格式檢查不是內容檢查；由B指出具體不支持處 |

        選讀短例連回run_agent的`casefold`、`split`、`join`及`json.dumps(sort_keys=True)`。
        record_counts的sum逐項加總布林判斷：True算1、False算0；下方也用相同工具清單作短例。
        這些操作只為辨認相同動作，不會修正模型答案。JSON序列化與set在前週出現過，這裡看它們在本週的用途即可。
    ''')
    code("syntax", text_block('''
        import json

        # 對應run_agent的normalized：只用來查重，不覆寫原搜尋字詞。
        query_demo = "  FORMS   Submit "
        normalized_demo = " ".join(query_demo.casefold().split())
        print("正規化：", normalized_demo)
        print("固定欄位順序：", json.dumps({"scope": "Streamlit", "query": normalized_demo}, sort_keys=True))
        print("原字詞仍在：", repr(query_demo))
        # 對應record_counts：逐筆看工具名稱，相符算1、不符算0。
        names_demo = ["search_official", "read_official_page", "search_official"]
        print("搜尋次數：", sum(name == "search_official" for name in names_demo))
    '''))
    md("homework", '''
        ## 13 作業、完成檢核與第15週

        課後45～60分鐘，沿同一App自選Python或Streamlit官方問題，保留正常／不足兩筆真實紀錄，完成A、B、一個離線停止／錯誤案例、11-1讀回及自己的README。
        真實紀錄可沿用課堂；服務失敗照實填，帳號／額度／網路問題列待補，由教師安排補測或共看，離線示意不能代替。
        繳學生Notebook、App、兩筆JSON或失敗說明、B與README；沿用學期Repo及已登記表單，依公告提交，不另登記每週資料夾連結。

        | 評量 | 比例 |
        |---|---:|
        | A與流程 | 40% |
        | B與來源證據、下載讀回 | 30% |
        | 錯誤與修正 | 20% |
        | 可重現與限制 | 10% |

        - [ ] 我能對應工具提案、執行、觀察與下一輪。
        - [ ] A七筆通過，Notebook與App相同；未完成不請求。
        - [ ] 我能分清外層、搜尋後端、內建搜尋與HTTP次數。
        - [ ] 我有真實紀錄或誠實失敗說明，並完成一筆主張與原文核對。
        - [ ] App下載已回11-1檢查，API開關預設False，沒有金鑰或教師答案混入學生骨架。

        第15週再談MCP如何提供外部工具，以及部署、Secrets、成本與專題測試。本週不新增部署作業。
        Agents SDK、多Agent、長期記憶與任意爬取列自主選讀，不列本週必交。
        官方依據：[Function Calling](https://developers.openai.com/api/docs/guides/function-calling)、[Web search](https://developers.openai.com/api/docs/guides/tools-web-search)、[Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)、[HTTPX](https://www.python-httpx.org/quickstart/)。
    ''')
    return annotate_dependencies(cells, PREFIX, CELL_NOUNS, direct_prereq=True)


UI = '''
# ========== App：先畫面、再表單提交，rerun與下載不請求 ==========
from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

PACKAGE = Path(__file__).resolve().parents[1]
load_dotenv(PACKAGE / ".env")
load_dotenv(Path(__file__).resolve().parent / ".env")
st.set_page_config(page_title="有限步數的官方文件助手", layout="centered")

def read_setting(name, default=""):
    """name為設定名稱str，default為缺值預設；平台Secrets優先，不顯示金鑰。"""
    try:
        value = st.secrets.get(name)
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        value = None
    return str(value if value is not None else os.getenv(name, default)).strip()

st.title("有限步數的官方文件助手")
st.caption("搜尋 → 看觀察 → 選頁閱讀 → 回答或說明不足。最多4輪、3次工具、6次Responses。")
st.session_state.setdefault("agent_record", None)
st.session_state.setdefault("agent_context", None)
api_on = st.checkbox("啟用真實API", value=False, key="api_on")
scope = st.selectbox("官方範圍", list(SCOPES), index=1, key="scope")
model = read_setting("OPENAI_MODEL", "gpt-5.4-mini")
context = (api_on, scope, model)
if st.session_state.agent_context != context:
    st.session_state.agent_record = None
    st.session_state.agent_context = context

if not api_on:
    st.info("離線只重播手寫情境及測A，0次API、0次HTTP；不是真實搜尋結果。")
    fixture = json.loads((PACKAGE / "sample_data/offline_traces.json").read_text(encoding="utf-8"))
    case = st.selectbox("手寫情境", list(fixture["cases"]), key="case")
    st.dataframe(fixture["cases"][case], hide_index=True)

with st.form("agent_form"):
    question = st.text_area("問題", value="在Streamlit表單裡，修改輸入值和按下提交按鈕，分別何時讓程式重新執行？請找官方依據。", key="question")
    submitted = st.form_submit_button("執行本次任務", type="primary")
if st.button("清除結果", key="clear"):
    st.session_state.agent_record = None
if submitted:
    # 新提交一開始就清舊紀錄；任何預檢或服務失敗都不顯示前次成功。
    st.session_state.agent_record = None
    try:
        if not 1 <= len(question.strip()) <= 300:
            raise ValueError("問題須為1至300字元")
        check_a()
        if not api_on:
            st.success("A七筆檢查通過；上方為手寫情境，沒有搜尋或模型答案。")
        else:
            key = read_setting("OPENAI_API_KEY")
            if not key:
                raise ValueError("缺少OPENAI_API_KEY；請設定本機.env或平台Secrets")
            with st.spinner("本次最多6次Responses；正在執行有限任務…"):
                with OpenAI(api_key=key, max_retries=0, timeout=60) as client:
                    st.session_state.agent_record = run_agent(client, question, scope, model)
    except NotImplementedError:
        st.warning("請完成student/app.py的TODO A，儲存後再提交；0次API。")
    except (ValueError, AssertionError) as exc:
        st.error(str(exc))

record = st.session_state.agent_record
if record is not None:
    st.subheader("本次結果")
    st.write("停止原因：", STOP_LABELS[record["stop_reason"]])
    st.json(record["counts"])
    if record["final"] is not None:
        st.write(record["final"]["answer"])
        for sid in record["final"]["source_ids"]:
            source = record["sources"][sid]
            st.link_button(f"{sid}：{source['title']}", source["url"])
    else:
        st.warning("本次停止，沒有成功答案；可下載失敗紀錄，請依原因查核。")
    # 任務完成後依序展示已記錄的步驟；展開只讀state，不重新請求。
    for event in record["trace"]:
        with st.expander(f"第{event['turn']}輪：{event.get('name', event['kind'])}"):
            st.json(event)
    with st.expander("來源、原文節錄與usage"):
        st.json({"sources": record["sources"], "requests": record["requests"]})
    st.download_button("下載本次agent_record.json", json.dumps(record, ensure_ascii=False, indent=2),
                       file_name="agent_record.json", mime="application/json", on_click="ignore")
    st.caption("下載後回Notebook第11-1節讀回；一致性通過仍須打開原文人工核對。")
'''


def app_source(teacher):
    role = "教師版" if teacher else "學生版"
    folder = "teacher" if teacher else "student"
    header = f'''# 第14週Agent官方文件查核助手（{role}）
# 用途：有限工具選擇、觀察、停止與來源查核；預設API關閉。
# 啟動：在week14/week14_agent執行 python -m streamlit run {folder}/app.py
# 真實提交最多6次Responses＋2次內建搜尋＋2次HTTP；max_retries=0、timeout=60。
# 生成來源：scripts/build_week14.py與scripts/templates/week14_agent_core.py。
'''
    sections = [STUDENT_A if name == "a" and not teacher else source
                for name, source in CORE.items() if name != "download_check"]
    return header + "\n\n".join(sections) + "\n" + UI


def reading_source(cells):
    parts = []
    for number, cell in enumerate(cells, 1):
        source = "".join(cell["source"])
        parts.append(f"<!-- 第{number}格 | {cell['id']} -->\n" +
                     (source if cell["cell_type"] == "markdown" else "```python\n"+source+"```\n"))
    return "\n".join(parts)


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    for teacher, role in [(False, "學生版"), (True, "教師版")]:
        cells = cells_for(teacher)
        book = {"nbformat": 4, "nbformat_minor": 5,
                "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                             "language_info": {"name": "python"}}, "cells": cells}
        stem = WEEK / f"{TITLE}_{role}"
        stem.with_suffix(".ipynb").write_text(json.dumps(book, ensure_ascii=False, indent=1)+"\n", encoding="utf-8")
        stem.with_suffix(".md").write_text(reading_source(cells), encoding="utf-8")
        folder = PACKAGE / ("teacher" if teacher else "student")
        (folder / ".streamlit").mkdir(parents=True, exist_ok=True)
        source = app_source(teacher)
        ast.parse(source)
        (folder / "app.py").write_text(source, encoding="utf-8")
        (folder / "requirements.txt").write_text(REQUIREMENTS, encoding="utf-8")
        (folder / ".streamlit/secrets.example.toml").write_text(
            'OPENAI_API_KEY = "your_api_key_here"\nOPENAI_MODEL = "gpt-5.4-mini"\n', encoding="utf-8")
    (PACKAGE / "requirements.txt").write_text(REQUIREMENTS, encoding="utf-8")
    (PACKAGE / ".env.example").write_text("OPENAI_API_KEY=your_api_key_here\nOPENAI_MODEL=gpt-5.4-mini\n", encoding="utf-8")
    (PACKAGE / ".gitignore").write_text(".env\n.venv*/\n**/.streamlit/secrets.toml\n**/__pycache__/\nagent_record*.json\n", encoding="utf-8")
    (PACKAGE / "sample_data").mkdir(exist_ok=True)
    (PACKAGE / "sample_data/offline_traces.json").write_text(json.dumps(
        {"mode": "離線手寫示意", "actual_api_requests": 0, "cases": OFFLINE}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (PACKAGE / "sample_data/demo_page.html").write_text(HTML, encoding="utf-8")
    print(f"第14週重建完成：每版{len(cells)}格；0次API，不覆蓋手寫文件。")


if __name__ == "__main__":
    main()
