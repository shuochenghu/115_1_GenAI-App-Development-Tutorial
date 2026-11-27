"""重建第14週修訂版學生／教師Notebook、閱讀稿、單檔App及離線資料；0次API。

核心來源：scripts/templates/week14_agent_core_revised.py；文字與配套由本檔生成。
不覆蓋手寫README、教師導讀、B表、工具契約或真實.env／Secrets。
Codex原版（build_week14.py、week14_agent/）保留不動。
"""
import ast
import json
from pathlib import Path
import re
from textwrap import dedent

from notebook_cell_notes import annotate_dependencies

ROOT = Path(__file__).resolve().parents[1]
WEEK = ROOT / "week14"
PACKAGE = WEEK / "week14_agent_revised"
TITLE = "生成式AI應用開發_第14週_Agent基礎與工作流程_修訂版"
PREFIX = "w14r-"
# 和第13週修訂版相同的版本，再加本週的httpx與Beautiful Soup。
REQUIREMENTS = ("streamlit==1.63.0\nopenai==2.49.0\npython-dotenv==1.2.3\n"
                "httpx==0.28.1\nbeautifulsoup4==4.14.3\n")
CORE = dict(re.findall(r"^# %% (\w+)\n(.*?)(?=^# %% |\Z)",
    (ROOT / "scripts/templates/week14_agent_core_revised.py").read_text(encoding="utf-8"), re.M | re.S))
CORE = {name: source.strip() + "\n" for name, source in CORE.items()}
STUDENT_A = CORE["a"][:CORE["a"].index("    # 教師完成參考")] + '''    # TODO A：依上面的規格，回傳擋下原因代號，或回傳None。
    # 提示：先判斷「這次是搜尋，而且搜尋次數已滿」，再判斷是否重複；上面的型別檢查保留。
    raise NotImplementedError("請完成TODO A：擋下規則，修改後重跑本格")
'''
NORMAL_QUESTION = "在Streamlit表單裡，修改輸入值和按下提交按鈕，分別何時讓程式重新執行？請找官方依據。"
OFFLINE = {
    "正常": [
        {"輪次": 1, "模型選擇": "搜尋", "參數": "Streamlit form submit rerun",
         "觀察": "手寫示意：候選s1、s2，只有搜尋摘要", "下一步": "讀s1原文"},
        {"輪次": 2, "模型選擇": "閱讀", "參數": "s1",
         "觀察": "手寫示意：讀到說明表單何時重新執行的段落", "下一步": "整理答案"},
        {"輪次": 3, "模型選擇": "回答", "參數": "answered，引用s1",
         "觀察": "手寫示意：答案只引用讀過的s1", "下一步": "結束"}],
    "不足與重查": [
        {"輪次": 1, "模型選擇": "搜尋", "參數": "Streamlit 2.0 release date",
         "觀察": "手寫示意：候選只有更新紀錄，沒有2.0日期", "下一步": "換一次關鍵字"},
        {"輪次": 2, "模型選擇": "搜尋", "參數": "Streamlit roadmap next major version",
         "觀察": "手寫示意：仍沒有確定日期", "下一步": "說明不足"},
        {"輪次": 3, "模型選擇": "回答", "參數": "insufficient，沒有引用",
         "觀察": "手寫示意：說明官方文件沒有支持的資料，不猜日期", "下一步": "結束"}],
    "重複後擋下": [
        {"輪次": 1, "模型選擇": "搜尋", "參數": "forms submit",
         "觀察": "手寫示意：候選s1", "下一步": "模型又提出相同字詞"},
        {"輪次": 2, "模型選擇": "搜尋（被擋下）", "參數": "Forms  Submit",
         "觀察": "repeated_action：沒有執行，之後不提供工具", "下一步": "只能整理答案"},
        {"輪次": 3, "模型選擇": "回答", "參數": "insufficient，沒有引用",
         "觀察": "手寫示意：只有搜尋摘要，沒讀原文，所以說明不足", "下一步": "結束"}],
    "搜尋已滿後擋下": [
        {"輪次": 1, "模型選擇": "搜尋", "參數": "st.form",
         "觀察": "手寫示意：沒有合適候選", "下一步": "換關鍵字"},
        {"輪次": 2, "模型選擇": "搜尋", "參數": "form submit button rerun",
         "觀察": "手寫示意：還是沒有合適候選", "下一步": "模型想再搜尋"},
        {"輪次": 3, "模型選擇": "搜尋（被擋下）", "參數": "streamlit form callback",
         "觀察": "search_limit：搜尋已滿2次，沒有執行", "下一步": "只能整理答案"},
        {"輪次": 4, "模型選擇": "回答", "參數": "insufficient，沒有引用",
         "觀察": "手寫示意：沒有讀到原文，說明不足", "下一步": "結束"}],
}
HTML = """<!doctype html><html lang="zh-TW"><body><nav>選單</nav><main>
<h1>手寫HTML抽取示意</h1><p>示意資料：表單內容在提交時送出。這不是下載的官方網頁。</p>
<script>這段不應放入本文</script></main><footer>頁尾</footer></body></html>"""
CELL_NOUNS = {
    "install": "安裝格", "colab": "Colab金鑰格", "imports": "匯入格", "policy": "規格格",
    "task": "搜尋規格格", "task-demo": "搜尋規格示範格", "html-demo": "HTML短例格",
    "reader": "閱讀工具格", "offline": "離線紀錄格", "protocol": "工具來回示意格",
    "a": "A格", "a-check": "A檢查函式格", "a-run": "A自我檢查格",
    "loop-demo": "迴圈短例格", "response": "回應檢查格", "search": "搜尋工具格",
    "record": "紀錄函式格", "runner": "Agent函式格", "live": "真實執行格",
    "save": "教師保存格", "download": "下載讀回格", "syntax": "語法短例格",
}


def text_block(text):
    return dedent(text).strip() + "\n"


def offline_source():
    """離線紀錄格：每一步拆成一行，投影時看得清楚。"""
    lines = ["# 手寫情境：不是模型或網路搜尋的結果。改case可以換看其他情境。",
             "offline_traces = {"]
    for case, steps in OFFLINE.items():
        lines.append(f"    {case!r}: [")
        lines.extend(f"        {step!r}," for step in steps)
        lines.append("    ],")
    lines += ["}",
              "",
              'case = "正常"   # 可改成"不足與重查"、"重複後擋下"或"搜尋已滿後擋下"',
              "for step in offline_traces[case]:",
              '    print(step["輪次"], step["模型選擇"], "｜", step["參數"], "｜", step["觀察"], "→", step["下一步"])',
              'print("手寫示意：本格0次API、0次HTTP")']
    return "\n".join(lines)


def cells_for(teacher):
    cells = []

    def md(tag, text):
        cells.append({"cell_type": "markdown", "id": PREFIX + tag, "metadata": {},
                      "source": text_block(text).splitlines(keepends=True)})

    def code(tag, source, requests=0):
        source = f"# 用途：{CELL_NOUNS[tag]}；先備：無；最多{requests}次API\n" + source.strip() + "\n"
        cells.append({"cell_type": "code", "id": PREFIX + tag,
                      "metadata": {"teaching": {"requires": [], "api_requests_max": requests}},
                      "source": source.splitlines(keepends=True), "outputs": [], "execution_count": None})

    role = "教師版" if teacher else "學生版"
    md("cover", f'''
        # 第14週｜Agent基礎與工作流程・修訂版（{role}）

        本週流程：**使用者提問→模型選工具→程式檢查並執行→把結果交回模型→模型再選下一步或回答→人工核對原文**。
        和前幾週的關係：第6週學過Structured Outputs，第13週學過Tool Calling的一次來回與內建搜尋；本週把「一次來回」放進有次數上限的迴圈，讓模型自己決定下一步。
        <font color="#C62828"><b>模型可以選下一步，但不能改範圍、提高次數或執行任意程式；這些都由程式決定。</b></font>
        安裝套件、讀取Colab金鑰與所有付費請求預設都關閉。離線手寫情境不是模型或搜尋的成果。課程模型沿用gpt-5.4-mini，帳號能否使用需在課前實測。
        {'教師版提供A的參考答案與B的判讀提示。' if teacher else '程式練習只有A；其餘函式完整提供，不需要重寫。'}
    ''')
    md("goals", '''
        ## 1 學習目標與150分鐘安排

        完成本週後，你能夠：
        - 說出Agent一輪中，模型、程式與人各自負責什麼。
        - 看懂「觀察→下一步」：工具結果怎麼影響模型的下一個選擇。
        - 寫出擋下工具的規則（A），並說明Agent為什麼一定要有上限。
        - 從工具路徑回查原文，判斷答案是否有根據（B）。

        | 核心時間 | 活動與產出 |
        |---|---|
        | 15分 | 從第13週固定兩步，到模型自己選下一步 |
        | 20分 | 兩個工具、HTML本文與離線紀錄 |
        | 15分 | 一次工具來回如何接到下一輪 |
        | 20分 | A：擋下規則與自我檢查 |
        | 30分 | 有限迴圈帶讀、教師真實示範 |
        | 35分 | A移入App、B原文查核、下載讀回 |
        | 15分 | 常見錯誤、作業與第15週 |

        另留休息10分鐘與排障20分鐘。程式練習只有A；B是查核紀錄。
    ''')
    md("environment", '''
        ## 2 環境與付費開關

        Notebook可以在Colab或本機執行；App要在本機用VS Code啟動，Colab不跑Streamlit。安裝方式見App的[README](week14_agent_revised/README.md)。
        下面兩格的INSTALL_PACKAGES與LOAD_COLAB_KEY預設False，直接全部執行也不會安裝套件或讀金鑰。
        本機的金鑰放在App資料夾的.env，第9節呼叫API時才讀取，和App共用同一份；金鑰不要寫進Notebook。
        **程式格開頭的註解：**「先備」是要先執行的格子；「用到前面格子定義的變數／函式」列出名稱與出處，例如`stop_reason ← 第7節A格`。出現NameError時，先回去執行那一格。
        <font color="#1565C0">費用提示：</font>搜尋除了token另有工具費。本課不寫固定價格，請依[官方計價](https://developers.openai.com/api/docs/pricing)與實際usage核對。
    ''')
    code("install", text_block('''
        INSTALL_PACKAGES = False   # 缺套件時才改成True
        if INSTALL_PACKAGES:
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "openai==2.49.0", "httpx==0.28.1",
                                   "beautifulsoup4==4.14.3", "python-dotenv==1.2.3"])
        else:
            print("預設不安裝；缺套件請參考App的README")
    '''))
    code("colab", text_block('''
        LOAD_COLAB_KEY = False   # 只在Colab且要呼叫API時改成True；金鑰不會顯示
        if LOAD_COLAB_KEY:
            import os
            from google.colab import userdata
            os.environ["OPENAI_API_KEY"] = userdata.get("OPENAI_API_KEY")
            print("已讀入本次runtime，未顯示金鑰")
        else:
            print("預設不讀Colab Secrets；本機會在第9節讀App資料夾的.env")
    '''))
    md("concept", '''
        ## 3 從第13週到第14週：誰決定下一步

        回想第13週的問題「Streamlit Community Cloud的requirements.txt要放哪裡？」：流程固定兩步，先prepare_search，再web_search，程式不管結果如何都只走這兩步。
        但真實查資料常常是這樣：搜尋結果只有標題清單，還不能回答；這時人會打開原文看，或換個關鍵字再找，找不到就老實說不足。
        這個「**看結果，再決定下一步**」就是本週的Agent。本週主要問題改用：

        > 在Streamlit表單裡，修改輸入值和按下提交按鈕，分別何時讓程式重新執行？

        這題光看搜尋摘要不夠，通常要讀原文的細節，比較能看出「觀察→下一步」。

        | 名詞 | 中文說法 | 在本週看什麼 |
        |---|---|---|
        | planning | 選下一步 | 模型這一輪選哪個工具、填什麼參數（不看隱藏推理） |
        | tool use | 使用工具 | 模型只是提出要求，Python檢查後才真的執行 |
        | observation | 觀察 | 工具交回的結果：候選頁面、原文片段，或錯誤訊息 |
        | final answer | 最後答案 | 依讀過的原文回答，或說明資料不足 |
        | stop | 停止 | 模型交出答案、程式擋下工具，或發生錯誤 |

        | 角色 | 負責 | 不負責 |
        |---|---|---|
        | 使用者 | 提問、選官方範圍 | 不替模型選工具 |
        | 外層模型 | 每一輪選搜尋、閱讀或回答 | 不能改範圍、不能提高次數 |
        | 程式 | 檢查提案、用A決定擋不擋、執行工具、記錄次數 | 不用eval執行模型的字串 |
        | 人 | 打開原文核對答案（B） | 不把「有引用」當成「答案正確」 |
    ''')
    md("layers", '''
        ### 3-1 兩層請求：先數清楚次數

        本週有兩種Responses請求，次數要分開數：
        1. **外層請求**：每一輪問一次模型「下一步做什麼」。最多4輪，第4輪不提供工具，只能回答。
        2. **搜尋請求**：模型選了搜尋，程式再送一次Responses，用內建web_search真的去搜（和第13週相同）。最多2次。

        閱讀工具不呼叫OpenAI，只是一般網頁HTTP。所以一題最多「4次外層＋2次搜尋＝6次Responses」，網頁HTTP最多2次。

        | 路徑 | 外層 | 搜尋 | Responses合計 | HTTP |
        |---|---:|---:|---:|---:|
        | 搜尋→閱讀→回答（最常見） | 3 | 1 | 4 | 1 |
        | 搜尋→換字詞再搜尋→閱讀→回答（最多） | 4 | 2 | 6 | 1 |
        | 不搜尋直接說明不足 | 1 | 0 | 1 | 0 |

        因為4輪裡最後一輪只能回答，所以一題最多執行3次工具。正常與不足兩題最多12次Responses；額外重跑另計。
    ''')
    md("tools-note", '''
        ## 4 兩個工具與資料分工

        | 工具 | 模型要填 | 程式做什麼 | 交回模型的觀察 |
        |---|---|---|---|
        | search_official | 英文關鍵字、範圍 | 送一次搜尋請求，只在官方網域搜 | 搜尋摘要、候選頁面代號s1、s2… |
        | read_official_page | 候選代號，例如s1 | 用HTTP讀該頁HTML，留下本文 | 原文片段，或讀不到的原因 |

        **搜尋摘要不是原文**：它是搜尋模型整理的線索；閱讀工具抓下來的片段才是網頁上的文字。所以本週規定：要回答，必須先讀過頁面。
        閱讀只能填候選代號、不能自己填網址，這樣模型就無法讓程式去讀任意網站。
        工具的寫法和第13週第6節的Skill對照相同：description說用途、INSTRUCTIONS定規則、parameters定輸入、Python函式負責執行。
        下面兩格只匯入套件與定義規格，0次API。
    ''')
    code("imports", CORE["imports"])
    code("policy", CORE["policy"])
    md("contract-note", '''
        ### 4-1 沿用第13週的搜尋規格

        build_search_task就是第13週的A：檢查關鍵字（1～80字元、不含網址）與範圍，回傳query及allowed_domains。本週直接提供，不用再寫。
        本週新增official_url，確認搜尋找到的網址真的在官方範圍：只接受https、官方主機本身（不含其他子網域）與預設埠。
        網址問號後的參數（例如`?view=full`）可能改變頁面內容，所以保留；`#`後面只是頁內位置，所以去掉，避免同一頁被當成兩頁。

        <font color="#2E7D32">預期觀察：</font>第一行印出query與allowed_domains；第二行網址保留`?view=full`、去掉`#submit`。
    ''')
    code("task", CORE["task"])
    code("task-demo", text_block('''
        task_demo = build_search_task("forms submit", "Streamlit")   # search_query="forms submit", scope="Streamlit"
        print(task_demo)
        print(official_url("https://docs.streamlit.io/develop/concepts/architecture/forms?view=full#submit", "Streamlit"))
    '''))
    md("html-note", '''
        ### 4-2 從HTML留下本文

        網頁除了本文，還有選單、頁尾與script。下面用一份手寫HTML，看程式怎麼只留下本文；這只是本機處理，沒有下載網頁。
        - `BeautifulSoup(html, "html.parser")`：第一個參數是HTML文字，第二個是Python內建的解析方式。
        - `select("script,style,nav,…")`找出這些標籤，`decompose()`把它們刪掉。
        - `get_text("\\n", strip=True)`取出文字，每段用換行隔開，並去掉前後空白。

        <font color="#2E7D32">預期觀察：</font>只印出標題與段落兩行；「選單」「頁尾」與script的文字都不見了。
    ''')
    code("html-demo", 'html_demo = ' + repr(HTML) + "\n\n" + text_block('''
        soup_demo = BeautifulSoup(html_demo, "html.parser")
        for element in soup_demo.select("script,style,nav,header,footer,aside,noscript"):
            element.decompose()   # 刪掉不是本文的標籤
        print(soup_demo.find("main").get_text("\\n", strip=True))
    '''))
    md("reader-note", '''
        ### 4-3 閱讀工具（完整提供）

        read_official_page用上一格同樣的方法處理真正的官方網頁，另外加上幾個限制：只讀一次、最多1MB、等待10秒、不跟轉址、不執行JavaScript，最後節錄前6000字元。
        它回傳dict：讀到就是`ok=True`和excerpt（原文片段）、sha256（片段的雜湊，下載後用來確認沒被改過）；讀不到就是`ok=False`和error。
        讀不到時，結果一樣交回模型，讓它改讀別頁或說明不足。<font color="#C62828"><b>「這次讀不到」不等於「官方沒有寫」。</b></font>
        定義這個函式不會連網；第9節或App真的執行時才會用到。
    ''')
    code("reader", CORE["reader"])
    md("trace-note", '''
        ## 5 先看離線紀錄：觀察怎麼決定下一步

        知道兩個工具後，先看四份手寫紀錄。它們沒有發任何請求，也不代表真實模型一定這樣走。
        看每一列時，問自己：**這一輪的觀察，為什麼讓模型選了下一步？**
        - 正常：搜尋只有摘要→讀原文→回答。
        - 不足與重查：第一次沒找到→換關鍵字→還是沒有→說明不足。
        - 重複後擋下、搜尋已滿後擋下：程式擋下工具，模型只能用已有資料收尾。

        <font color="#2E7D32">預期觀察：</font>印出「正常」的3輪。改case再執行，可以看其他情境。
    ''')
    code("offline", offline_source())
    md("trace-observe", '''
        ### 5-1 讀完紀錄後回答

        - 「正常」有3輪外層、2次工具；最後回答也算一輪，但不算工具。
        - 兩個「擋下」情境裡，被擋下的那一步沒有執行，所以不算工具次數；擋下後，模型還能交出「說明不足」的答案，不會什麼都沒有。
        - 想一想：如果閱讀失敗，答案應該寫「讀不到」還是「官方沒有寫」？後者需要更多證據。
    ''')
    md("protocol-note", '''
        ## 6 一次工具來回如何接到下一輪

        這部分和第13週第10節相同，只是本週會重複好幾輪。每一輪：
        1. 模型提出function_call：name是工具名稱，arguments是**JSON字串**，call_id是這次呼叫的編號。
        2. 程式檢查後執行工具，得到觀察。
        3. 下一輪的input＝前面的歷史＋這一輪模型的完整輸出＋function_call_output（用同一個call_id，output放觀察的JSON字串）。

        ```mermaid
        flowchart LR
            M[模型選工具] --> V[程式檢查提案<br>A決定擋不擋]
            V --> T[執行白名單工具]
            T --> O[同call_id交回觀察]
            O --> M
        ```

        下一格用手寫的閱讀提案與失敗觀察，組出下一輪要送的input；0次API，不需要先完成A。
        <font color="#2E7D32">預期觀察：</font>arguments的型別是str；印出3筆資料，最後一筆的call_id和function_call相同。
    ''')
    code("protocol", text_block('''
        demo_call = {"type": "function_call", "name": "read_official_page",
                     "call_id": "call_demo_1", "arguments": '{"source_id": "s1"}'}
        demo_observation = {"ok": False, "source_id": "s1", "error": "手寫示意：頁面需要轉址"}

        demo_history = [{"role": "user", "content": "手寫示意：請查Streamlit表單何時重新執行"}]
        demo_history.append(demo_call)                                  # 這一輪模型的輸出
        demo_history.append({"type": "function_call_output",
                             "call_id": demo_call["call_id"],           # 同一個call_id
                             "output": json.dumps(demo_observation, ensure_ascii=False)})  # output是字串
        print("arguments的型別：", type(demo_call["arguments"]).__name__)
        for number, item in enumerate(demo_history, 1):
            print(number, json.dumps(item, ensure_ascii=False))
    '''))
    md("a-note", '''
        ## 7 A：什麼時候要擋下工具

        如果模型一直搜尋、或一直重複同一個動作，就會不斷花錢卻沒有進展。所以每次執行工具前，程式都要先問A：「這個工具可以執行嗎？」
        本週有兩條擋下規則：搜尋最多2次；和之前完全相同的動作不再執行。被擋下後，程式會告訴模型原因，之後的輪次不再提供工具，模型只能用已有資料回答或說明不足。

        已提供：輸入型別檢查。你負責：完成判斷並回傳結果。

        | 項目 | 規格 |
        |---|---|
        | search_count | 這題已經執行的搜尋次數，非負整數 |
        | max_searches | 搜尋上限，正整數；run_agent傳LIMITS["searches"]，也就是2 |
        | tool_name | 這次要執行的工具："search_official"或"read_official_page" |
        | is_repeat | 這次工具與參數是否和之前相同；run_agent已經算好，傳入True或False |
        | 回傳 | 這次是搜尋且search_count已達上限→"search_limit"；否則若重複→"repeated_action"；其他→None |
        | 兩條都成立 | 回傳"search_limit"（上限優先） |

        注意：「已達上限」是search_count等於或大於max_searches，例如已搜尋2次、上限2，第3次就要擋下。閱讀不受搜尋上限影響。
        一定要用return回傳，只用print，run_agent拿不到結果。完成後重跑本格，再執行7-1的兩格。
    ''')
    code("a", CORE["a"] if teacher else STUDENT_A)
    md("a-check-note", '''
        ### 7-1 A自我檢查

        check_a用8筆固定情境測試stop_reason，回傳檢查紀錄list；不要修改它來讓答案通過。
        A還沒完成時只會顯示提示，a_checks保持None，不影響前面的示範；第9節與App也會在送出請求前先跑check_a。

        <font color="#2E7D32">預期觀察：</font>完成A時印出「A自我檢查通過：8筆」與每筆情境；判斷錯誤時，錯誤訊息會指出是哪個情境、應回傳什麼。
    ''')
    code("a-check", CORE["a_check"])
    code("a-run", text_block('''
        a_checks = None
        try:
            a_checks = check_a()
            print("A自我檢查通過：", len(a_checks), "筆；0次API")
            for item in a_checks:
                print(item)
        except NotImplementedError as exc:
            print(exc)
    '''))
    md("a-observe", '''
        ### 7-2 檢查通過代表什麼

        8筆涵蓋：一般放行、剛好達到上限、閱讀不受搜尋上限影響、重複搜尋與重複閱讀、兩條同時成立，以及把上限改成1。
        通過只代表「規則照規格運作」，不代表模型會選對工具，也不代表答案正確。
        比較「已搜尋1次」和「已搜尋2次」：前者放行，後者擋下。擋在**執行前**，第3次搜尋才不會先花錢再發現超額。
        除了A，迴圈本身也有上限：4輪中最後一輪不提供工具。所以就算模型一直想用工具，一題最多也只有6次Responses。
    ''')
    md("loop-note", '''
        ## 8 把一次來回放進有限迴圈

        先用手寫短例看迴圈怎麼控制，再讀完整程式。短例裡模型想連搜3次：
        - `range(1, 5)`產生1～4輪；`allow_tools`在第4輪或擋下後變成False。
        - 第3次搜尋被擋下，`tools_open`改成False，`continue`直接進下一輪。
        - 第4輪不提供工具，只能回答，`break`離開迴圈。

        <font color="#2E7D32">預期觀察：</font>印出4輪，第3輪顯示擋下，第4輪回答。把planned改成`["搜尋", "閱讀", "回答"]`，第3輪就會回答並結束。
    ''')
    code("loop-demo", text_block('''
        # 手寫的模型選擇，只用來看迴圈怎麼控制；沒有呼叫模型。
        planned = ["搜尋", "搜尋", "搜尋", "回答"]
        searches = 0
        tools_open = True
        for turn in range(1, 5):
            allow_tools = tools_open and turn < 4          # 最後一輪或擋下後，不提供工具
            choice = planned[turn - 1] if allow_tools else "回答"
            if choice == "回答":
                print(f"第{turn}輪：允許工具={allow_tools}，模型回答，結束")
                break
            if choice == "搜尋" and searches >= 2:          # 對應A的search_limit
                tools_open = False
                print(f"第{turn}輪：想再搜尋，但已搜尋2次→擋下，之後只能回答")
                continue
            if choice == "搜尋":
                searches += 1
            print(f"第{turn}輪：允許工具={allow_tools}，執行{choice}（已搜尋{searches}次）")
        print("實際API 0次")
    '''))
    md("response-note", '''
        ### 8-1 先檢查回應，才執行

        下面三個檢查函式完整提供，都是0次API。和第12、13週一樣，先看拒答與完成狀態，再看內容。

        | 函式 | 傳入 | 回傳 |
        |---|---|---|
        | check_response(response) | SDK回應物件 | 沒有回傳值；拒答丟出"refused"，未完成丟出"incomplete" |
        | read_function_call(response, scope, sources) | 本輪回應、使用者範圍、已登記的候選頁面 | (call, arguments)；模型沒提工具時回傳(None, None) |
        | check_final(data, sources) | 最後答案dict、候選頁面 | 檢查通過的data |

        read_function_call只接受一個提案、只認兩個工具名稱，範圍不能換，閱讀只能填登記過的代號。
        check_final要求三個欄位：status（answered或insufficient）、answer、source_ids。answered至少要引用一個**成功讀到**的頁面；它只檢查格式與引用，內容對不對要靠B。
    ''')
    code("response", CORE["response"])
    md("search-note", '''
        ### 8-2 搜尋工具：額外一次請求

        search_official(client, search_query, scope, record)把第13週的內建搜尋包成一個工具：client是已設定好的OpenAI連線，search_query與scope是檢查過的參數，record是本題紀錄。
        送出的參數和第13週第16節選讀相同：web_search只在allowed_domains內搜尋、tool_choice強制搜尋、max_tool_calls=1只搜一次、include要求附上查閱過的頁面。
        `store=False`只是不保存這次回應，問題仍會送到API。
        搜尋到的網址會登記成s1、s2…，存在record["sources"]，閱讀工具只能讀這些頁面。沒找到就回傳空的候選清單，不會補造網址。
    ''')
    code("search", CORE["search"])
    md("record-note", '''
        ### 8-3 每一步都記下來

        new_record建立本題紀錄dict；record_counts從逐步紀錄重算次數。記錄方式有兩個原則：
        - **送出前先記**：請求逾時，伺服器仍可能已經處理，所以不能當作0次。
        - **拿不到用量就留None**：不能寫成0，否則看起來像免費。

        紀錄裡的trace是每一輪發生的事（執行工具、被擋下、最後答案或停止），requests是每一次Responses請求。下載到Notebook檢查與B查核，都用這份紀錄。
    ''')
    code("record", CORE["record"])
    md("runner-note", '''
        ### 8-4 完整Agent：分五段閱讀

        run_agent(client, question, scope, model)把前面的函式接起來，回傳本題紀錄dict。程式裡用①～⑤標出五段：

        | 段落 | 做什麼 | 要注意 |
        |---|---|---|
        | ① 預檢 | 檢查問題、範圍，跑check_a | A沒完成就在這裡停下，0次API |
        | ② 外層請求 | 問模型下一步 | tool_choice="auto"讓模型自己選；最後一輪或擋下後，不提供工具 |
        | ③ 看提案 | 用read_function_call檢查 | 沒有提案＝最後答案，用check_final檢查後結束 |
        | ④ A決定 | 算出是否重複，呼叫stop_reason | 放行就執行工具；擋下就把原因當作觀察，之後關閉工具 |
        | ⑤ 交回觀察 | 歷史加上這輪完整輸出與function_call_output | 完整輸出可能含reasoning項目，要原樣帶回；畫面不顯示 |

        「重複」的判斷：搜尋字詞先轉小寫、去掉多餘空白，再和工具名稱一起變成一個字串（action_key），放進used_actions集合；同一個action_key再出現就是重複。
        API錯誤（例如逾時、429）不會自動重送，因為OpenAI連線設定max_retries=0；紀錄會寫下錯誤類別，然後停止。
    ''')
    code("runner", CORE["runner"])
    md("live-note", '''
        ## 9 真實API：先確認A，再開啟本格

        先備：第4、7、8節的定義格都已執行，A自我檢查通過。把本格的RUN_AGENT改成True後執行一次。
        - 本機：先把App資料夾的`.env.example`複製成`.env`並填入金鑰（見App的README）；本格會讀它，和App共用。
        - Colab：先執行第2節的Colab金鑰格。
        - 每次執行最多6次Responses、2次內建搜尋、2次網頁HTTP。`timeout=60`是每次請求的等待上限，不是整題的總時間。
        - 本格一開始先把agent_record設為None，失敗時不會留下上一次的結果。

        <font color="#2E7D32">預期觀察：</font>印出結束原因、次數、每一輪做了什麼，最後是答案與引用。路徑每次可能不同，不必剛好是搜尋→閱讀→回答。
    ''')
    code("live", text_block(f'''
        import os

        from dotenv import load_dotenv
        from openai import OpenAI

        RUN_AGENT = False   # 改成True才會真的呼叫API
        agent_record = None
        question = "{NORMAL_QUESTION}"
        scope = "Streamlit"
        if RUN_AGENT:
            try:
                check_a()                                   # A沒通過就在這裡停下，0次API
                load_dotenv("week14_agent_revised/.env")    # 本機：先讀App資料夾的.env（和App共用）
                load_dotenv()                               # 再找目前資料夾往上的.env
                api_key = os.getenv("OPENAI_API_KEY", "").strip()
                if not api_key or api_key == "your_api_key_here":
                    raise ValueError("缺少OPENAI_API_KEY；本機設定.env，Colab先執行金鑰格")
                model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
                with OpenAI(api_key=api_key, max_retries=0, timeout=60) as client:
                    agent_record = run_agent(client, question, scope, model)
                print("結束原因：", STOP_LABELS[agent_record["stop_reason"]])
                print("次數：", agent_record["counts"])
                for event in agent_record["trace"]:
                    print(f"第{{event['turn']}}輪", event["kind"], event.get("name", ""), event.get("reason", ""))
                if agent_record["final"] is not None:
                    print("答案：", agent_record["final"]["answer"])
                    print("引用：", agent_record["final"]["source_ids"])
            except (NotImplementedError, AssertionError, ValueError) as exc:
                print("尚未送出請求：", exc)
        else:
            print("RUN_AGENT=False：0次API，沒有產生答案")
    '''), 6)
    md("save-note", '''
        ### 9-1 選用：教師保存本次紀錄

        只有第9節真的產生了agent_record才會保存；失敗紀錄也照實保存。預設關閉，0次新增API。
        紀錄不含金鑰或reasoning，但會有問題原文，公開前先確認內容可以分享。學生用App下載即可，不需要這格。
    ''')
    code("save", text_block('''
        import json
        from pathlib import Path

        SAVE_TEACHER_RECORD = False
        if SAVE_TEACHER_RECORD and agent_record is not None:
            Path("agent_record.json").write_text(json.dumps(agent_record, ensure_ascii=False, indent=2), encoding="utf-8")
            print("已保存agent_record.json；0次新增API")
        else:
            print("本格未保存：未開啟，或本次沒有紀錄")
    '''))
    md("b-note", '''
        ## 10 B：從工具路徑回查原文

        完成兩筆紀錄：一題「正常」問題、一題「可能不足」的問題。不預設模型一定答對或一定查不到，照實際結果記錄；課堂做過的紀錄可以直接用，不必為了湊步數重跑。
        建議題目：正常題用第9節的表單問題；不足題可問「Streamlit官方文件有沒有公布2.0版的確定發布日期？」（和第13週的不足題同類型）。

        在[B紀錄表](week14_agent_revised/觀察與查核紀錄.md)依序填：
        1. 每一輪的選擇、參數與觀察，寫出「下一步為什麼這樣選」。
        2. 選答案裡一個具體主張→找它引用的source_id→看紀錄中的excerpt→打開該網址→核對原文是否支持。
        3. 再核對一個版本、日期或數字。網頁沒寫日期就填「未標示」；讀取時間只是我們何時讀，不是網頁日期。

        錯誤或邊界情況可以用離線情境說明，不要刻意花API製造錯誤。**格式與引用檢查通過，不代表內容正確。**
    ''' + ('''

        <font color="#6A1B9A"><b>教師判讀提示（虛構示意，非API成果）：</b></font>學生只寫「找到表單文件」還不夠，要寫出主張、來源代號、對應原文短句與適用條件。
        若讀取失敗，合格的說法是「這次沒有取得可用本文」，不能推論「官方沒有說」。實際路徑沒有重查，就寫「沒有重查」。
    ''' if teacher else ""))
    md("app-note", '''
        ## 11 把同一個A放進App

        依[App的README](week14_agent_revised/README.md)建立環境並啟動student/app.py，把Notebook完成的stop_reason貼到App的同名函式；其他函式和Notebook完全相同，不用另寫。
        - **API未啟用（預設）**：可以選四種手寫情境看步驟；按「執行本次任務」只會跑A的8筆檢查。0次API。
        - **API啟用**：一次提交就跑完整題，最多6次Responses。完成後用表格顯示每一輪做了什麼，原始紀錄放在展開區。
        - 缺金鑰、A未完成、問題空白或超過300字元，都在送出前停止，0次API。
        - 切換範圍、切換API、按清除或新提交失敗，都會清掉舊結果；一般rerun、展開與下載不會重新請求。
    ''')
    md("download-note", '''
        ### 11-1 下載後重新讀回

        在App按「下載本次agent_record.json」，把檔案放到Notebook所在的資料夾（Colab：拖進左側「檔案」窗格），再執行下一格。這格自帶需要的程式，0次API，不必先跑前面的格子。
        它依序檢查：是修訂版App的真實紀錄、最後一筆是結束事件、call_id不重複且閱讀的頁面都先搜尋過、次數和逐步紀錄相同、原文片段沒被改過、答案只引用讀到的頁面。
        通過只代表「紀錄前後接得起來」，不能證明答案正確；B仍要打開原文核對。第二份下載檔可能叫`agent_record (1).json`，改path後再執行。

        <font color="#2E7D32">預期觀察：</font>印出「紀錄一致性檢查通過」與次數；沒有檔案時只提示。檢查失敗時，中文訊息會指出哪一項不一致。
    ''')
    code("download", CORE["download_check"] + "\n\n" + text_block('''
        import json
        from pathlib import Path

        downloaded_record = None
        path = Path("agent_record.json")
        if path.is_file():
            downloaded_record = json.loads(path.read_text(encoding="utf-8"))
            print("紀錄一致性檢查通過：", check_record(downloaded_record))
            print("最後狀態：", downloaded_record["run_status"], "；請繼續到B打開原文核對")
        else:
            print("尚未找到agent_record.json：先從App下載並放到目前資料夾，再執行本格。0次API")
    '''))
    md("syntax-note", '''
        ## 12 常見錯誤與語法回查

        | 現象 | 回查 |
        |---|---|
        | 改完A還顯示未完成 | 重跑第7節A格，再跑7-1；App要存檔後再提交 |
        | 缺少OPENAI_API_KEY | 本機檢查App資料夾的.env；Colab先執行金鑰格。金鑰不要貼進程式 |
        | 工具提案不合規格（invalid_call） | 工具名稱、範圍、候選代號、call_id是否重複 |
        | 最後答案不合規格（invalid_final） | answered有沒有引用成功讀到的頁面；三個欄位是否齊全 |
        | 讀取轉址或沒有本文 | 本週不跟轉址、不跑JavaScript；在B寫下限制，不改成任意爬取 |
        | 答案和原文不符 | 程式只檢查格式與引用，由B指出哪裡不支持 |

        run_agent判斷重複時用到幾個字串與JSON操作，下一格用短例對照：
        - `casefold()`轉小寫、`split()`以空白切開（多個空白也只算一個）、`" ".join(...)`再用一個空格接回去。
        - `json.dumps(..., sort_keys=True)`讓dict的欄位固定照字母排序，同樣的參數一定得到同樣的字串。
        - record_counts的`sum(條件 for ...)`：True算1、False算0，加起來就是符合條件的筆數。
    ''')
    code("syntax", text_block('''
        import json

        # 對應run_agent的normalized：只用來判斷重複，原本的搜尋字詞仍照原樣保存。
        query_demo = "  FORMS   Submit "
        normalized_demo = " ".join(query_demo.casefold().split())
        print("正規化後：", repr(normalized_demo))
        print("固定欄位順序：", json.dumps({"scope": "Streamlit", "search_query": normalized_demo}, sort_keys=True))

        # 對應record_counts：逐筆看工具名稱，相符算1、不符算0。
        names_demo = ["search_official", "read_official_page", "search_official"]
        print("搜尋次數：", sum(name == "search_official" for name in names_demo))
    '''))
    md("homework", '''
        ## 13 課後作業與驗收

        課後45～60分鐘，沿用同一個App，從Python或Streamlit選一個方向，自訂兩個不含個資或機密的問題（一正常、一可能不足）。
        繳交：學生Notebook、App、兩筆agent_record.json（用11-1讀回；失敗也照實記錄）、[B紀錄表](week14_agent_revised/觀察與查核紀錄.md)與自己的README。
        至少完成：
        - 寫出每一輪「觀察→下一步」的理由。
        - 核對一個主張是否被原文支持，以及一個版本、日期或數字。
        - 記錄一個擋下、錯誤或邊界情況（可用離線情境）：預期→實際→原因→處理。

        | 評量項目 | 比重 |
        |---|---:|
        | A的擋下規則與流程說明 | 40% |
        | B的路徑與原文查核、下載讀回 | 30% |
        | 錯誤修正與邊界說明 | 20% |
        | 可重現與限制說明 | 10% |

        請求次數：一題最多6次Responses；兩題最多12次。課堂完成的兩筆可以直接當作業；若重做，請另外記錄次數。
        沒有API額度時，先交離線情境與A的結果，真實欄位填「未測」，由老師安排共看；不要用手寫情境冒充真實結果。
        沿用學期Repo與已登記的表單；本週不新增部署要求。
    ''')
    md("next", '''
        ## 14 完成檢核與第15週

        - [ ] 我能說出Agent一輪中，模型、程式與人各自負責什麼。
        - [ ] 我能分清外層請求、搜尋請求與網頁HTTP，並算出一題的請求次數。
        - [ ] A的8筆檢查通過；Notebook與App的A相同，A未完成時不會送出請求。
        - [ ] 我知道搜尋摘要不是原文，「讀不到」也不等於「官方沒有寫」。
        - [ ] 下載的紀錄已用11-1讀回，並在B完成一個主張的原文核對。

        第15週會談MCP如何提供外部工具，以及部署、Secrets、成本與專題測試；本週的工具契約、紀錄與擋下規則都會沿用。
        Agents SDK、多Agent、長期記憶與任意爬取屬自主選讀，不列本週必交。
        官方文件：[Function calling](https://developers.openai.com/api/docs/guides/function-calling)、[Web search](https://developers.openai.com/api/docs/guides/tools-web-search)、[Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)、[HTTPX](https://www.python-httpx.org/quickstart/)。
    ''')
    return annotate_dependencies(cells, PREFIX, CELL_NOUNS, direct_prereq=True)


UI = '''
# ========== App：先畫面、再表單提交；rerun、展開與下載都不會送請求 ==========
from pathlib import Path
import os

from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

PACKAGE = Path(__file__).resolve().parents[1]
load_dotenv(PACKAGE / ".env")                          # 本機：App資料夾的.env
load_dotenv(Path(__file__).resolve().parent / ".env")
st.set_page_config(page_title="有限步數的官方文件助手", layout="centered")


def read_setting(name, default=""):
    """讀設定：Streamlit Cloud的Secrets優先，其次環境變數／.env；不顯示金鑰。"""
    try:
        value = st.secrets.get(name)
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        value = None
    return str(value if value is not None else os.getenv(name, default)).strip()


def trace_rows(record):
    """把本題trace整理成表格列；只讀紀錄，不送請求。"""
    rows = []
    for event in record["trace"]:
        if event["kind"] == "tool":
            observation = event["observation"] or {}
            if event["name"] == "search_official":
                result = f"候選{len(observation.get('candidates', []))}頁（搜尋摘要，不是原文）"
            else:
                result = "讀到原文片段" if observation.get("ok") else observation.get("error", "沒有結果")
            rows.append({"輪次": event["turn"], "類型": "執行工具", "內容": event["name"],
                         "參數": json.dumps(event["arguments"], ensure_ascii=False), "結果": result})
        elif event["kind"] == "blocked":
            rows.append({"輪次": event["turn"], "類型": "程式擋下", "內容": event["name"],
                         "參數": json.dumps(event["arguments"], ensure_ascii=False),
                         "結果": STOP_LABELS[event["reason"]] + "，之後只能回答"})
        elif event["kind"] == "final":
            final = event["result"]
            rows.append({"輪次": event["turn"], "類型": "最後答案", "內容": final["status"],
                         "參數": "、".join(final["source_ids"]) or "沒有引用", "結果": STOP_LABELS[final["status"]]})
        else:
            rows.append({"輪次": event["turn"], "類型": "停止", "內容": event["reason"],
                         "參數": "", "結果": STOP_LABELS[event["reason"]]})
    return rows


# 1. 畫面與設定；切換模式、範圍或模型時清掉舊結果
st.title("有限步數的官方文件助手")
st.caption("模型每一輪選：搜尋、閱讀或回答。最多4輪、搜尋2次、6次Responses；最後一輪只能回答。")
st.session_state.setdefault("agent_record", None)
st.session_state.setdefault("agent_context", None)
api_on = st.checkbox("啟用真實API", value=False, key="api_on")
scope = st.selectbox("官方範圍", list(SCOPES), index=1, key="scope")
model = read_setting("OPENAI_MODEL", "gpt-5.4-mini")
context = (api_on, scope, model)
if st.session_state.agent_context != context:
    st.session_state.agent_record = None
    st.session_state.agent_context = context

# 2. 離線：只看手寫情境，按提交只跑A的檢查
if not api_on:
    st.info("離線模式：下表是手寫情境，不是真實搜尋結果；按「執行本次任務」只會跑A的8筆檢查。0次API。")
    fixture = json.loads((PACKAGE / "sample_data/offline_traces.json").read_text(encoding="utf-8"))
    case = st.selectbox("手寫情境", list(fixture["cases"]), key="case")
    st.dataframe(fixture["cases"][case], hide_index=True)

# 3. 表單：改文字不會送出，按提交才執行
with st.form("agent_form"):
    question = st.text_area("問題", value=QUESTION, key="question")
    submitted = st.form_submit_button("執行本次任務", type="primary")
if st.button("清除結果", key="clear"):
    st.session_state.agent_record = None
if submitted:
    st.session_state.agent_record = None   # 新提交先清舊紀錄，失敗時不顯示上一次的答案
    try:
        if not 1 <= len(question.strip()) <= 300:
            raise ValueError("問題須為1至300字元")
        check_a()
        if not api_on:
            st.success("A的8筆檢查通過；離線模式沒有搜尋，也沒有模型答案。")
        else:
            key = read_setting("OPENAI_API_KEY")
            if not key or key == "your_api_key_here":
                raise ValueError("缺少OPENAI_API_KEY；請設定本機.env或Streamlit Cloud的Secrets")
            with st.spinner("最多6次Responses；正在執行…"):
                with OpenAI(api_key=key, max_retries=0, timeout=60) as client:
                    st.session_state.agent_record = run_agent(client, question, scope, model)
    except NotImplementedError:
        st.warning("請完成app.py的TODO A，存檔後再提交；0次API。")
    except (ValueError, AssertionError) as exc:
        st.error(str(exc))

# 4. 顯示本次結果：只讀session_state，不重新請求
record = st.session_state.agent_record
if record is not None:
    st.subheader("本次結果")
    st.write("結束原因：", STOP_LABELS[record["stop_reason"]])
    counts = record["counts"]
    st.write(f"外層{counts['turns']}輪、工具{counts['tools']}次（搜尋{counts['searches']}、閱讀{counts['reads']}）、"
             f"Responses共{counts['api_requests']}次、網頁HTTP {counts['http_requests']}次")
    st.dataframe(trace_rows(record), hide_index=True)
    if record["final"] is not None:
        st.write(record["final"]["answer"])
        for sid in record["final"]["source_ids"]:
            source = record["sources"][sid]
            st.link_button(f"{sid}：{source['title']}", source["url"])
    else:
        st.warning("本次停止，沒有合格答案；可下載紀錄，依結束原因查核。")
    with st.expander("候選頁面與原文片段"):
        st.json(record["sources"])
    with st.expander("原始紀錄（trace與requests）"):
        st.json({"trace": record["trace"], "requests": record["requests"]})
    st.download_button("下載本次agent_record.json", json.dumps(record, ensure_ascii=False, indent=2),
                       file_name="agent_record.json", mime="application/json", on_click="ignore")
    st.caption("下載後回Notebook第11-1節讀回；一致性通過後，仍要打開原文填B表。")
'''


def app_source(teacher):
    role = "教師版" if teacher else "學生版"
    folder = "teacher" if teacher else "student"
    header = f'''# 第14週修訂版Agent官方文件查核助手（{role}）
# 教學重點：模型自己選搜尋、閱讀或回答；程式用A擋下超額與重複，並記錄每一步。
# 啟動：在week14/week14_agent_revised執行 python -m streamlit run {folder}/app.py
# 預設API關閉；真實提交一題最多6次Responses＋2次內建搜尋＋2次網頁HTTP，max_retries=0、timeout=60。
# 生成來源：scripts/build_week14_revised.py與scripts/templates/week14_agent_core_revised.py，不要手改本檔。
'''
    sections = [STUDENT_A if name == "a" and not teacher else source
                for name, source in CORE.items() if name != "download_check"]
    question = f"\nQUESTION = {NORMAL_QUESTION!r}\n"
    return header + "\n\n".join(sections) + question + UI


def reading_source(cells):
    parts = []
    for number, cell in enumerate(cells, 1):
        source = "".join(cell["source"])
        parts.append(f"<!-- 第{number}格 | {cell['id']} -->\n" +
                     (source if cell["cell_type"] == "markdown" else "```python\n" + source + "```\n"))
    return "\n".join(parts)


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    for teacher, role in [(False, "學生版"), (True, "教師版")]:
        cells = cells_for(teacher)
        book = {"nbformat": 4, "nbformat_minor": 5,
                "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                             "language_info": {"name": "python"}}, "cells": cells}
        stem = WEEK / f"{TITLE}_{role}"
        stem.with_suffix(".ipynb").write_text(json.dumps(book, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
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
        {"mode": "離線手寫示意", "actual_api_requests": 0, "cases": OFFLINE}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (PACKAGE / "sample_data/demo_page.html").write_text(HTML, encoding="utf-8")
    print(f"第14週修訂版重建完成：每版{len(cells)}格；0次API，不覆蓋手寫文件。")


if __name__ == "__main__":
    main()
