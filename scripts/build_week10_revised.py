"""重建第10週修訂版學生／教師教材與App；不安裝套件、不呼叫API。

原課堂簡化版（build_week10_simple.py與week10_semantic_search_simple）保留不動。
修訂重點：資料改用第9週sample.txt清理後文字並統一問題、補「意思相近→向量相近」直覺、
離線規則與真實向量對照、教師課前實測紀錄、B紀錄表預填列、用語與排版。
"""
import json
from pathlib import Path
from textwrap import dedent

from notebook_cell_notes import annotate_dependencies

ROOT = Path(__file__).resolve().parents[1]
WEEK = ROOT / "week10"
PACKAGE = WEEK / "week10_semantic_search_revised"
WEEK09_SAMPLE = ROOT / "week09/sample_tata/sample.txt"   # 第9週範例原檔（唯一來源）
TITLE = "生成式AI應用開發_第10週_Embedding與語意搜尋_課堂簡化版_修訂版"
PREFIX = "w10r-"


def block(text):
    return dedent(text).strip() + "\n"


def week09_cleaned_text():
    """與第9週clean_text相同規則：統一換行、逐行合併空白、最多保留一個空白行。"""
    import re
    text = WEEK09_SAMPLE.read_bytes().decode("utf-8-sig")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [" ".join(line.split()) for line in normalized.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


DOC = week09_cleaned_text()
QUESTIONS = [
    {"type": "原句", "query": "活動地點在哪裡？", "expected_chunk_id": 0, "evidence": "地點為圖書館討論室"},
    {"type": "改寫", "query": "這場讀書交流辦在哪個空間？", "expected_chunk_id": 0, "evidence": "地點為圖書館討論室"},
    {"type": "資訊未提供", "query": "參加費用是多少？", "expected_chunk_id": 2, "evidence": "報名網址與費用尚未提供"},
    {"type": "文件外", "query": "火星的平均氣溫是多少？", "expected_chunk_id": None, "evidence": None},
]

DEMO = block('''
    def demo_vector(text):
        """完整提供：人工指定4組關鍵字計數，不是模型學到的語意向量。"""
        groups = [
            ["地點", "圖書館", "討論室", "哪裡"],   # 第1維：地點
            ["報名", "截止"],                       # 第2維：報名
            ["名額", "每組", "人數", "幾人"],       # 第3維：人數
            ["費用", "多少錢", "網址"],             # 第4維：費用與網址
        ]
        vector = []
        for words in groups:
            vector.append(float(sum(text.count(word) for word in words)))
        return vector
''')

COSINE = block('''
    def cosine_similarity(a, b):
        """完整提供：計算方向相似度；零向量回傳0，不能解讀為有語意證據。"""
        import math   # 放在函式內：Notebook與App可單獨複製這個函式使用
        if not a or len(a) != len(b):
            raise ValueError("向量不可為空且維度必須相同")
        if not all(type(x) in (int, float) and math.isfinite(x) for x in a + b):
            raise ValueError("向量必須是有限數字")
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return max(-1.0, min(1.0, dot / (norm_a * norm_b)))
''')

RANK_COMMON = '''
    def rank_chunks(chunks, vectors, query_vector, top_k=3, min_score=0.0):
        """傳入片段與同順序向量，回傳附score的來源資料；不呼叫API。"""
        # 已提供：參數與資料檢查。
        if type(top_k) is not int or top_k <= 0:
            raise ValueError("top_k須為正整數")
        if not isinstance(min_score, (int, float)) or not -1 <= min_score <= 1:
            raise ValueError("min_score須介於-1與1")
        if len(chunks) != len(vectors):
            raise ValueError("片段與向量筆數不一致")
        if not chunks:
            return []
        # 已提供：先確認向量都能計算；問題向量全零就回傳空結果，不硬塞一筆。
        for vector in vectors:
            cosine_similarity(vector, query_vector)
        if not any(query_vector):
            return []
'''
RANK_TEACHER = block(RANK_COMMON + '''
        # 教師完成參考：對應學生TODO A，保留來源並依原始分數篩選、排序。
        results = []
        for item, vector in zip(chunks, vectors):
            score = cosine_similarity(vector, query_vector)
            if score >= min_score:
                hit = dict(item)          # 複製一份，不改到原本的chunks
                hit["score"] = score
                results.append(hit)
        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:top_k]
''')
RANK_STUDENT = block(RANK_COMMON + '''
        # TODO A：
        # 1. 逐筆用cosine_similarity算出score；score >= min_score才保留。
        # 2. 用dict(item)複製來源資料，再加入"score"欄位（不可改到原本的chunks）。
        # 3. 依score由高到低排序，回傳前top_k筆；沒有合格片段就回傳[]。
        raise NotImplementedError("請完成TODO A：來源保留、篩選與排序")
''')

READ_SETTING = block('''
    def read_setting(name, default=""):
        """完整提供：平台Secrets優先，本機使用環境變數或本資料夾的.env。"""
        try:
            return st.secrets.get(name, os.getenv(name, default))
        except FileNotFoundError:
            return os.getenv(name, default)
''')

APP = block('''
    # ---------- 2. 模式與成功資料 ----------
    st.title("文件片段搜尋")
    st.caption("先找支持問題的原文，不生成答案。請勿輸入個資、機密或未授權內容。")
    real_api = st.checkbox("使用真實Embeddings API（可能產生費用）", value=False)
    st.caption("預設是離線關鍵字規則，不是語意模型；換句話說的問題可能找不到。真實模式每次有效提交最多1次API。")
    st.session_state.setdefault("record", None)
    st.session_state.setdefault("error", "")
    # 切換模式時，舊結果來自另一種向量，直接清除
    if st.session_state.get("real_api_mode") != real_api:
        st.session_state.record = None
        st.session_state.error = ""
        st.session_state.real_api_mode = real_api
    if st.button("清除結果"):
        st.session_state.record = None
        st.session_state.error = ""

    # ---------- 3. 表單：貼入第9週確認過的文字與問題 ----------
    # 預設文字＝第9週sample.txt清理後的結果；也可貼上第9週App下載的cleaned_text.txt內容。
    sample = (Path(__file__).resolve().parents[1] / "sample_data/week09_cleaned_text.txt").read_text(encoding="utf-8")
    with st.form("search_form"):
        source = st.text_area("文件文字（空白行分段；可貼第9週的清理後文字）", value=sample, height=210)
        query = st.text_input("查詢問題（範例見sample_data/questions.json）", value="活動地點在哪裡？")
        submitted = st.form_submit_button("建立向量並搜尋")

    if submitted:
        st.session_state.record = None  # 新提交失敗時，不能沿用舊的成功資料。
        st.session_state.error = ""
        try:
            # ---------- 4. 輸入檢查與分段：全在本機 ----------
            source = source.replace("\\r\\n", "\\n").replace("\\r", "\\n")
            if not source.strip() or len(source) > 6000:
                raise ValueError("文件須有1到6000字元，不會默默截斷")
            if not query.strip() or len(query) > 300:
                raise ValueError("問題須有1到300字元")
            chunks = []
            cursor = 0
            for paragraph in source.split("\\n\\n"):
                text = paragraph.strip()
                if text:
                    if len(text) > 1000:
                        raise ValueError("每段最多1000字元，請先確認並分段")
                    start = source.find(text, cursor)   # 記下這段在貼入文字中的位置
                    end = start + len(text)
                    chunks.append({
                        "chunk_id": len(chunks), "source": "貼入文字",
                        "start": start, "end": end, "text": text,
                    })
                    cursor = end
            if len(chunks) > 12:
                raise ValueError("最多12段，請縮小教學文件範圍")
            # 付費前先試跑A：A未完成會在這裡停止，0次API。
            rank_chunks([{"chunk_id": 0, "source": "檢查", "text": "檢查"}], [[1.0]], [1.0])
            inputs = [item["text"] for item in chunks] + [query]

            # ---------- 5. 文件與問題用同一種向量 ----------
            if real_api:
                key = read_setting("OPENAI_API_KEY")
                if not key:
                    raise ValueError("缺少OPENAI_API_KEY，請設定.env或平台Secrets")
                model = read_setting("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
                # 小型教學批次：文件＋問題合併成1次請求；每次新提交都重新向量化。
                # 正式服務應保存文件向量，之後只向量化新問題；本例不做跨次快取。
                with OpenAI(api_key=key, max_retries=0, timeout=60.0) as client:
                    response = client.embeddings.create(
                        model=model, input=inputs, encoding_format="float",
                    )
                # 依index排回送出的順序，再檢查筆數、維度與數值
                ordered = sorted(response.data, key=lambda item: item.index)
                if [item.index for item in ordered] != list(range(len(inputs))):
                    raise ValueError("向量回傳筆數或順序不合格")
                vectors = [item.embedding for item in ordered]
                for vector in vectors:
                    if not vector or len(vector) != len(vectors[0]) or not any(vector):
                        raise ValueError("向量為空、全零或維度不一致")
                    if not all(type(x) in (int, float) and math.isfinite(x) for x in vector):
                        raise ValueError("向量含非有限數字")
                mode = "真實Embeddings API"
            else:
                vectors = [demo_vector(text) for text in inputs]
                model = "人工關鍵字4維；非語意模型"
                mode = "離線規則示範"
            # 兩種向量不可混用；保存本次原文、模型與同批向量，供滑桿在本機重排。
            st.session_state.record = {
                "mode": mode, "model": model, "source": source,
                "query": query, "chunks": chunks, "vectors": vectors,
            }
        except NotImplementedError as exc:
            st.session_state.error = str(exc)
        except ValueError as exc:
            st.session_state.error = str(exc)
        except Exception as exc:
            st.session_state.error = "本次未保存結果，請檢查模型、網路或額度。錯誤類型：" + type(exc).__name__

    # ---------- 6. 只在本機重排：改滑桿不會再呼叫API ----------
    top_k = st.slider("最多顯示幾段（top_k）", 1, 5, 2)
    min_score = st.slider("最低分數（不是正確機率）", 0.0, 1.0, 0.0, 0.05)
    if st.session_state.error:
        st.error(st.session_state.error)
    if st.session_state.record is not None:
        record = st.session_state.record
        try:
            hits = rank_chunks(
                record["chunks"], record["vectors"][:-1],
                record["vectors"][-1], top_k, min_score,
            )
            st.caption("以下為上次成功提交的結果；表單改了但沒提交，原文與問題不會更新。")
            st.write("模式：", record["mode"], "模型：", record["model"])
            st.write("本次問題：", record["query"])
            if not hits:
                st.warning("沒有可用片段；請檢查關鍵字規則、門檻與原文，不能補造答案。")
            for item in hits:
                st.write(f"chunk {item['chunk_id']}｜分數 {item['score']:.4f}｜來源 {item['source']}｜位置 {item['start']}:{item['end']}")
                st.write(item["text"])
            with st.expander("核對本次原文"):
                st.text(record["source"])
            # 只匯出原文與排名結果；不寫入金鑰或整批高維向量。
            export = {
                "mode": record["mode"], "model": record["model"],
                "query": record["query"], "source": record["source"],
                "top_k": top_k, "min_score": min_score, "hits": hits,
            }
            st.download_button(
                "下載搜尋紀錄", json.dumps(export, ensure_ascii=False, indent=2),
                "search_record.json", mime="application/json",
            )
        except (ValueError, NotImplementedError) as exc:
            st.error(str(exc))
''')


CELL_NOUNS = {   # 程式格的口語名稱；節次由前一個標題自動決定
    "install": "環境格", "data": "資料格", "cosine-fn": "cosine函式格", "cosine-example": "手寫向量計算格",
    "a": "A格", "a-check": "A自我檢查格", "demo-fn": "離線規則函式格", "offline-run": "離線對照格",
    "real-run": "真實API格", "real-rank": "真實排名格", "teacher-record-run": "教師紀錄格",
}
TAG_ALIASES = {"A": "a"}   # 舊寫法「先備：A」


def cells_for(teacher):
    cells = []

    def add(kind, tag, source, requires=()):
        cell = {"cell_type": kind, "id": PREFIX + tag, "metadata": {"teaching": {"requires": list(requires)}},
                "source": block(source).splitlines(keepends=True)}
        if kind == "code":
            cell.update(execution_count=None, outputs=[])
        cells.append(cell)

    def md(tag, text):
        add("markdown", tag, text)

    def code(tag, text, requires=()):
        add("code", tag, text, requires)

    edition = "教師版" if teacher else "學生版"
    question_rows = "\n            ".join(f'{{"type": "{q["type"]}", "query": "{q["query"]}"}},' for q in QUESTIONS)
    md("cover", f"""
        # 第10週｜Embedding與語意搜尋・修訂版（{edition}）

        本週流程：**已核對的片段 → 向量 → 相似度 → 找出相關片段 → 回到原文確認**。
        第9週處理資料品質；本週只負責「找資料」；第11週才根據找到的證據產生回答。
        <font color="#C62828"><b>重要：</b></font>相似度不是答案正確的機率；找到一段文字，也不代表它真的能回答問題。
        配套App見[README](week10_semantic_search_revised/README.md)。
    """)
    md("goals", """
        ## 0. 先備、學習目標與150分鐘安排

        先備：第2週list／dict、函式、sorted與lambda；第7週表單與session_state；第9週片段與來源回查。
        不需要先學NumPy矩陣、ChromaDB／FAISS，也不用再寫PDF／Word讀取程式。

        完成本週後，你能夠：
        - 說明「意思相近的句子，向量方向也會接近」，以及為什麼文件和問題要用同一個模型。
        - 讀懂cosine相似度，知道分數不是正確機率。
        - 完成A：把分數變成保留來源、可回查的排名結果。
        - 完成B：用原句、改寫、資訊未提供、文件外四種問題，判斷排名是否真的有原文支持。

        | 時間 | 核心活動 |
        |---|---|
        | 15分鐘 | 第9～11週地圖、從第9週接入資料 |
        | 20分鐘 | Embedding直覺與手寫小向量 |
        | 20分鐘 | cosine示範與分數判讀 |
        | 25分鐘 | A：來源保留、門檻與排序，自我檢查與修正 |
        | 25分鐘 | 離線規則對照、真實API示範（或教師實測紀錄）、B觀察 |
        | 30分鐘 | 把A移入App、改參數與來源核對 |
        | 15分鐘 | 互看、錯誤與作業說明 |

        合計150分鐘，另留休息10分鐘與排障20分鐘。必做A與B；只做一個App。
    """)
    md("setup", """
        ## 1. 環境、金鑰與費用

        - **在哪裡執行：**Notebook看概念與短例子；Streamlit App在本機VS Code終端機啟動。本機沿用Python 3.14；Colab的Python版本由平台決定。
        - **需要哪些套件：**相似度與排序只用Python內建模組；真實API與App需要openai、python-dotenv與streamlit，不需要向量資料庫。
        - **金鑰放哪裡：**本機放環境變數或`week10_semantic_search_revised/.env`（Notebook與App共用）；Colab在Secrets設定OPENAI_API_KEY並授權Notebook；App部署到Streamlit Cloud時在平台的Secrets設定。金鑰不要寫進Notebook或程式。
        - **會呼叫幾次API：**需要付費的格子都有自己的開關，預設關閉。Notebook的真實示範把3段文件與4個問題合成1次請求；App每次有效提交1次。
        - **不能放什麼資料：**真實模式會把文件與問題送到OpenAI，不可放個資、機密或未授權資料。
        - timeout=60是每次網路等待的秒數，不保證整個任務在60秒內結束。
        - **程式格開頭的註解：**「先備」是要先執行的格子（包含間接需要的）；「用到前面格子定義的變數／函式」列出這格直接用到的名稱與出處，例如`rank_chunks ← 第5節A格`；若有「模組：」那一行，是前面格子匯入的套件。出現NameError時，先回去執行那一格。
    """)
    code("install", """
        # 用途：顯示環境；先備：無；0次API。只有要用真實API或App時才需要安裝。
        # Colab：取消下一行註解後執行。本機：依README用python -m pip安裝。
        # %pip install openai==2.49.0 python-dotenv==1.2.3
        import sys
        print("Python：", sys.version)
    """)
    md("units", """
        ## 2. 從第9週接入：片段與來源

        本週資料直接沿用第9週：`sample.txt`經過清理後的文字（也就是第9週App「下載清理後文字」的內容）。
        依空白行分段，每一段當作一個片段（檢索單位），保留chunk_id與來源，之後才能回到原文核對。
        下一格把這份文字分成3段，並列出本週固定使用的4個問題；Notebook與App用的是同一份資料與問題。

        | 問題類型 | 問題 | 預期能支持答案的片段 |
        |---|---|---|
        | 原句 | 活動地點在哪裡？ | chunk 0（地點為圖書館討論室） |
        | 改寫 | 這場讀書交流辦在哪個空間？ | chunk 0（用字不同，意思相同） |
        | 資訊未提供 | 參加費用是多少？ | chunk 2（原文寫「費用尚未提供」） |
        | 文件外 | 火星的平均氣溫是多少？ | 沒有，整份文件都沒談這件事 |
    """)
    code("data", f'''
        # 用途：第9週清理後文字分段，並列出本週的4個問題；先備：無；0次API。
        document = {DOC!r}

        # 依空白行分段：每段一個片段，保留編號與來源（App用同樣的分法）
        chunks = []
        for paragraph in document.split("\\n\\n"):
            if paragraph.strip():
                chunks.append({{"chunk_id": len(chunks), "source": "第9週sample.txt", "text": paragraph.strip()}})

        questions = [
            {question_rows}
        ]
        for item in chunks:
            print(item["chunk_id"], repr(item["text"]))
    ''')
    md("embedding", """
        ## 3. Embedding：把文字變成可以比較的數字

        Embedding模型把一段文字轉成一串數字（向量）。關鍵直覺是：**意思相近的句子，向量的方向也會接近**；所以即使用字不同（「在哪裡」和「哪個空間」），也可能找到同一段。
        - 文件和問題必須用**同一個模型**轉成向量，維度相同才能比較。
        - Embeddings API只回傳向量；它不會建立資料庫、不會找來源，也不會產生回答。

        先用手寫的2維向量建立直覺。假設維度1代表「和地點有關的程度」、維度2代表「和費用有關的程度」：

        | 句子 | 手寫向量（地點, 費用） |
        |---|---|
        | 問題：活動在哪裡？ | (1.0, 0.1) |
        | 地點為圖書館討論室 | (0.9, 0.2) |
        | 報名網址與費用尚未提供 | (0.1, 0.9) |
        | 每組4人，總名額32人 | (0.2, 0.3) |

        這些數字是人工設定的，只為了教「方向」；真實模型的向量有上千維，每一維也沒有可以直接讀懂的意義。
    """)
    md("cosine", """
        ## 4. Cosine相似度：比較方向，不是正確率

        cosine＝兩個向量的內積 ÷ 兩個長度的乘積，範圍約在−1到1：方向相同接近1，互相垂直是0。
        它不是機率：0.8不代表「答案80%正確」，也沒有適用所有資料的固定門檻。
        下一格的cosine_similarity完整提供；再下一格用第3節的手寫向量算一次，看看「問地點」最接近哪一句。
    """)
    md("syntax", """
        ### 4-1 讀程式需要的短語法

        | 語法 | 在cosine_similarity或A的哪裡 | 做什麼 |
        |---|---|---|
        | `zip(a, b)` | `dot = sum(x * y for x, y in zip(a, b))` | 把兩個向量的數字一對一配對；先檢查長度，避免zip悄悄截短 |
        | `sum(... for ...)` | 同上 | 把每一對乘積加總，不必先建立完整list |
        | `all(...)`、`math.isfinite` | 檢查有限數字那一行 | 每個數字都要是有限值，排除NaN或無限大 |
        | `any(vector)` | A的已提供檢查 | 至少有一個數字不是0；全零代表沒有方向 |
        | `dict(item)` | A的TODO | 複製一份片段資料，再加score，避免改到原本的chunks |
        | `results[:top_k]` | A的TODO | 取前k筆；不足k筆時就回傳現有的筆數 |
        | `key=lambda item: item["score"]` | A的TODO | 排序時依score排；`reverse=True`由高到低（第2週學過） |
    """)
    code("cosine-fn", "# 用途：完整提供的cosine相似度（App使用同一個函式）；先備：無；0次API。\n\n\n" + COSINE)
    code("cosine-example", """
        # 用途：用第3節的手寫向量算相似度；先備：cosine-fn；0次API。
        question = [1.0, 0.1]                         # 問題：活動在哪裡？
        sentences = {
            "地點為圖書館討論室": [0.9, 0.2],
            "報名網址與費用尚未提供": [0.1, 0.9],
            "每組4人，總名額32人": [0.2, 0.3],
        }
        for text, vector in sentences.items():
            print(f"{cosine_similarity(question, vector):.3f}", text)

        # 邊界：全零向量沒有方向，回傳0，不代表語意已被理解
        print("全零向量：", cosine_similarity([0.0, 0.0], [1.0, 0.0]))
    """, ["cosine-fn"])
    md("cosine-result", """
        預期「地點為圖書館討論室」最高（約0.99），「費用」那句最低。方向接近就是分數高，這正是語意搜尋的基本原理。
        但「每組4人」也有約0.6的分數：分數高低是相對的，不能看到正數就當成有關，還是要回原文判斷。
    """)
    md("ranking", """
        ## 5. A：把分數變成可回查的排名（必做，約20分鐘含修正）

        | 項目 | 說明 |
        |---|---|
        | 已提供 | 參數檢查（top_k、min_score、筆數）、向量可計算的檢查、問題向量全零時回傳[] |
        | 你負責 | ① 逐筆算score；② score ≥ min_score才保留；③ 用dict(item)複製並加score；④ 由高到低排序；⑤ 取前top_k筆 |
        | 輸入 | chunks（list[dict]）、同順序的vectors、query_vector、top_k、min_score |
        | 回傳 | list[dict]，每筆保留原來源欄位並多一個score；沒有合格片段就回傳[] |
        | 結果保存 | 下一格自我檢查把結果存到hits_result |
        | 執行順序 | 第4節cosine函式格 → A格 → A自我檢查格；App使用同一個函式 |

        要用return回傳，只print的話後面拿不到；不可直接在原本的dict加score。排序語法見4-1。
    """)
    code("a", "# 用途：練習A排名函式（App使用同一個函式）；先備：cosine-fn；0次API。\n\n\n"
         + (RANK_TEACHER if teacher else RANK_STUDENT), ["cosine-fn"])
    code("a-check", """
        # 用途：A自我檢查（固定資料，不需修改）；先備：cosine-fn、A；0次API。
        hits_result = None
        try:
            check_chunks = [
                {"chunk_id": 10, "source": "測試.txt", "text": "第一段"},
                {"chunk_id": 11, "source": "測試.txt", "text": "第二段"},
                {"chunk_id": 12, "source": "測試.txt", "text": "第三段"},
            ]
            check_vectors = [[0.0, 1.0], [1.0, 0.0], [0.8, 0.6]]
            hits_result = rank_chunks(check_chunks, check_vectors, [1.0, 0.0], 2, 0.5)
            assert [item["chunk_id"] for item in hits_result] == [11, 12]   # 由高到低、門檻與top_k
            assert all(item["source"] == "測試.txt" for item in hits_result)  # 來源保留
            assert "score" not in check_chunks[0]                             # 原資料沒被改
            assert rank_chunks(check_chunks, check_vectors, [1.0, 0.0], 5, 0.99) == hits_result[:1]  # 門檻很高只剩1筆
            assert rank_chunks(check_chunks, check_vectors, [0.0, 0.0]) == []  # 全零問題
            print("A通過：排序、門檻、top_k、來源保留與不修改原資料")
        except NotImplementedError as exc:
            print(exc)
    """, ["cosine-fn", "a"])
    md("a-result", """
        A應顯示通過訊息。常見錯誤：
        - 順序反了：檢查reverse。
        - 原資料被改：是不是直接在原本的dict加了score。
        - 筆數不對：檢查篩選與切片的順序（先篩選、再排序、最後取前k筆）。

        請保留一次「失敗→修正→重測」，或另外設計一筆空結果的邊界資料。通過自我檢查只證明程式功能正確，不代表語意搜尋品質好。
    """)
    md("offline", """
        ## 6. 離線對照：人工關鍵字規則

        沒有金鑰時，可以先用demo_vector跑通流程：它把文字中出現的關鍵字分4組計數，**不是模型學出來的語意向量**。
        下一格用第2節的4個問題跑一次，請特別注意「改寫」那題：原文寫「地點」，問題寫「哪個空間」，規則沒收這些字，就會找不到。
        離線規則與真實向量不能混用，分數也不能互相比較。
    """)
    code("demo-fn", "# 用途：完整提供的離線規則向量（App使用同一個函式）；先備：無；0次API。\n\n\n" + DEMO)
    code("offline-run", """
        # 用途：用離線規則跑4個問題；先備：data、cosine-fn、A、demo-fn；0次API。
        offline_results = None
        try:
            vectors = [demo_vector(item["text"]) for item in chunks]
            offline_results = []
            for q in questions:
                hits = rank_chunks(chunks, vectors, demo_vector(q["query"]), top_k=2, min_score=0.1)
                offline_results.append({"type": q["type"], "query": q["query"], "hits": hits})
                found = [(hit["chunk_id"], round(hit["score"], 3)) for hit in hits]
                print(q["type"], q["query"], "→", found or "找不到")
        except NotImplementedError as exc:
            offline_results = None   # 未完成A時不保留一半的結果
            print(exc)
    """, ["data", "cosine-fn", "a", "demo-fn"])
    md("offline-result", """
        預期：原句與費用題找得到；**改寫題找不到**（問題裡沒有規則收錄的關鍵字，向量全是0）；文件外題也找不到。
        這說明關鍵字比對的限制：用字不同就失效。下一節用真實Embedding，看看同一個改寫問題能不能找到chunk 0。
    """)
    md("real", """
        ## 7. 真實Embeddings API：同一批文件與問題

        下一格把第2節的3段文件與4個問題，用同一個模型一次轉成向量。RUN_REAL_EMBEDDINGS預設False（0次）；改成True後執行一次是1次請求，不會產生回答。
        1. 7段文字（3段文件＋4個問題）一次送出。
        2. 回傳的每筆有index，依index排回原本的順序。
        3. 前3個是文件向量，後4個是問題向量；檢查筆數、維度、數值都合格才保存embedding_result，失敗會清掉舊資料。

        資料很小，所以合成一批送出；實務上會保存文件向量，之後只需要向量化新問題。官方說明：[Embeddings](https://developers.openai.com/api/docs/guides/embeddings)。
    """)
    code("real-run", """
        # 用途：同一模型一次向量化3段文件與4個問題；先備：data；預設0次API，開啟後1次。
        import math
        import os
        import sys

        RUN_REAL_EMBEDDINGS = False   # 改成True才會真的呼叫API
        embedding_result = None
        embedding_error = None
        documents = [item["text"] for item in chunks]
        query_texts = [q["query"] for q in questions]

        if RUN_REAL_EMBEDDINGS:
            try:
                from dotenv import load_dotenv
                from openai import OpenAI

                # 1. 讀金鑰：本機用環境變數或App資料夾的.env（與App共用）；在Colab則讀Secrets
                load_dotenv("week10_semantic_search_revised/.env")   # 先讀App資料夾的.env
                load_dotenv()                                         # 再找目前資料夾往上的.env
                key = os.getenv("OPENAI_API_KEY", "")
                if "google.colab" in sys.modules:
                    from google.colab import userdata
                    key = userdata.get("OPENAI_API_KEY")
                if not key:
                    raise ValueError("請先設定並授權OPENAI_API_KEY")

                # 2. 文件＋問題合成一批，用同一個模型送出（1次請求）
                model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
                inputs = documents + query_texts
                with OpenAI(api_key=key, max_retries=0, timeout=60.0) as client:
                    response = client.embeddings.create(model=model, input=inputs, encoding_format="float")

                # 3. 依index排回原順序，再檢查筆數、維度與數值
                ordered = sorted(response.data, key=lambda item: item.index)
                if [item.index for item in ordered] != list(range(len(inputs))):
                    raise ValueError("回傳向量筆數或順序不合格")
                vectors = [item.embedding for item in ordered]
                for vector in vectors:
                    if not vector or len(vector) != len(vectors[0]):
                        raise ValueError("向量為空或維度不一致")
                    if not all(type(x) in (int, float) and math.isfinite(x) for x in vector) or not any(vector):
                        raise ValueError("向量含非有限數字或全零")
                embedding_result = {"model": model, "documents": documents,
                                    "questions": query_texts, "vectors": vectors}
                print("已保存真實向量：", len(vectors), "筆，每筆", len(vectors[0]), "維")
            except Exception as exc:
                embedding_error = f"本次未保存向量：{type(exc).__name__}：{exc}"
                print(embedding_error)
        else:
            print("RUN_REAL_EMBEDDINGS=False：已略過API，尚未取得真實語意向量")
    """, ["data"])
    md("real-result", """
        ### 7-1 用真實向量排名4個問題

        下一格用剛才保存的向量排名，不會再呼叫API；沒有執行真實API時只會提示「未測」，不會用離線規則冒充。
        先寫下你預期每題會找到哪一段，再看結果；特別比較「改寫」題和第6節離線規則的差別。
        文件外的問題仍然會有一個最高分的片段，要回到原文判斷它是不是真的能回答。

        老師課前實跑時，可把SAVE_TEACHER_RECORD改成True，存下排名紀錄（不含向量）供沒有API的同學觀察。
    """)
    code("real-rank", """
        # 用途：用已保存的真實向量排名；先備：data、cosine-fn、A、real-run；0次新API。
        import json
        from datetime import datetime, timezone
        from pathlib import Path

        SAVE_TEACHER_RECORD = False   # 老師課前實測時改成True，存成teacher_ranking_record.json
        real_rankings = None
        if embedding_result is None:
            print("尚未取得真實向量：B的真實語意觀察寫「未測」，或看7-2的教師實測紀錄")
        else:
            try:
                count = len(embedding_result["documents"])
                real_chunks = [{"chunk_id": i, "source": "第9週sample.txt", "text": text}
                               for i, text in enumerate(embedding_result["documents"])]
                real_rankings = []
                for offset, query in enumerate(embedding_result["questions"]):
                    hits = rank_chunks(real_chunks, embedding_result["vectors"][:count],
                                       embedding_result["vectors"][count + offset], 2, 0.0)
                    real_rankings.append({"query": query, "hits": hits})
                    print(query, "→", [(hit["chunk_id"], round(hit["score"], 3)) for hit in hits])
                if SAVE_TEACHER_RECORD:
                    record = {"note": "教師課前實測紀錄，不是本次執行結果",
                              "recorded_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                              "model": embedding_result["model"], "rankings": real_rankings}
                    Path("teacher_ranking_record.json").write_text(
                        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
                    print("已存teacher_ranking_record.json（不含向量）")
            except NotImplementedError as exc:
                print(exc)
    """, ["data", "cosine-fn", "a", "real-run"])
    md("teacher-record", """
        ### 7-2 沒有API時：看老師課前的實測紀錄

        如果老師有提供teacher_ranking_record.json，把它放在Notebook所在的資料夾，執行下一格就能看到真實Embedding的排名。
        這是**老師的實測紀錄**，請在B表的「模式」欄寫「教師實測紀錄（日期、模型）」，不要寫成自己執行的結果。
        沒有這個檔案時，B的真實語意欄寫「未測」即可。
    """)
    code("teacher-record-run", """
        # 用途：讀老師課前存下的真實排名紀錄；先備：teacher_ranking_record.json在目前資料夾；0次API。
        import json
        from pathlib import Path

        teacher_record = None
        path = Path("teacher_ranking_record.json")
        if path.exists():
            teacher_record = json.loads(path.read_text(encoding="utf-8"))
            print(teacher_record["note"], "｜", teacher_record["recorded_at_utc"], "｜", teacher_record["model"])
            for item in teacher_record["rankings"]:
                print(item["query"], "→", [(hit["chunk_id"], round(hit["score"], 3)) for hit in item["hits"]])
        else:
            print("沒有教師實測紀錄：B的真實語意欄寫「未測」")
    """)
    md("b", """
        ## 8. B：同一份資料，四種問題與兩組參數（必做觀察）

        TODO B：沿用同一份資料，不另寫第二個搜尋器。把結果填入8-1的表格：
        1. 四種問題各記一列：預期片段、實際排名與分數、原文是否支持。沒有證據就寫「不足」。
        2. 固定一個問題，只改一個參數（top_k=1與2，或兩個不同門檻），記下哪些片段增加或消失。
        3. 記一次錯誤或邊界與處理，例如問題空白、規則全零、門檻太高全部排除、API失敗；不能補造模型結果。

        Notebook的排名重用已保存的向量、App的滑桿在本機重排，都不會再呼叫API；只有送出新文字或新問題才會多算一次。
        沒有API時，可用離線規則加上7-2的教師實測紀錄完成；兩者都要標明模式。
    """)
    teacher_note = """

        <font color="#6A1B9A">教師提醒：</font>真實排名請課前實跑後再說明，不要在學生版預填順序。離線規則的改寫題本來就會全零，這是規則限制，不是學生做錯。
        評分優先看原文是否支持與比較條件是否固定，不按最高分數加分；合理判斷「資訊不足」也是有效成果。
    """ if teacher else ""
    md("b-reference", """
        ### 8-1 B紀錄表

        | 問題類型 | 模式（離線／自己的API／教師實測） | 預期片段 | 實際chunk_id與分數 | 原文是否支持／限制 |
        |---|---|---|---|---|
        | 原句：活動地點在哪裡？ | 待填 | chunk 0 | 待填 | 待填 |
        | 改寫：這場讀書交流辦在哪個空間？ | 待填 | chunk 0 | 待填 | 待填 |
        | 資訊未提供：參加費用是多少？ | 待填 | chunk 2 | 待填 | 待填 |
        | 文件外：火星的平均氣溫是多少？ | 待填 | 沒有 | 待填 | 待填 |
        | 參數比較（同一題，k或門檻二選一） | 待填 | — | 待填 | 待填 |

        分數高卻沒有原文支持，要記為「檢索不足」，不能拿來生成肯定的答案。
        「資訊未提供」和「文件外」要分清楚：前者原文明確寫了「尚未提供」，後者整份文件根本沒談這件事。
    """ + teacher_note)
    md("app", """
        ## 9. 把A移入同一個Streamlit App

        student/app.py只有A待完成：把通過自我檢查的rank_chunks貼到同名函式。cosine、離線規則與畫面都已提供。
        - App的預設文字就是第2節的第9週清理後文字；也可以貼上自己第9週App下載的cleaned_text.txt。以空白行分段，最多12段。
        - 每個片段保留start／end，可回到貼入的文字核對位置。App不會匯入第9週的JSON。
        - 預設離線模式0次API；勾選真實模式後，每次有效提交1次請求（文件與問題合成一批）。改top_k或門檻滑桿只在本機重排，不會再呼叫API。
        - 表單改了但沒提交，畫面仍是上次成功結果；切換模式、清除或新提交失敗都會清掉舊結果。A未完成時不會送出付費請求。
        - 下載的搜尋紀錄包含模式、模型、原文、問題與排名，不含金鑰與整批向量。這是小文件教學App，不是正式的大型索引。
    """)
    md("homework", """
        ## 10. 回家作業：同一個App的搜尋證據（45～60分鐘）

        沿用A與同一個App，換一份合法、無敏感資料的小文件（可用自己第9週作業的清理後文字），或自己寫3～6段虛構內容。題目自選，最低要求固定。
        1. 用原句、改寫、文件外三種問題各搜尋一次；至少一題找到支持來源，一題判斷證據不足。
        2. 固定同一題，比較兩組top_k或門檻，說明理由，並下載兩份搜尋紀錄JSON。
        3. 記錄一個錯誤或邊界的預期、實際、修正與重測；人工核對一個日期或數字。

        繳交：學生Notebook（A自我檢查＋B紀錄表）、同一個App、文件或貼入文字、兩份搜尋紀錄JSON、README。截圖或文字證據擇一即可。
        請求次數：老師示範1次；你在App問三種問題各1次，共3次。改滑桿與下載不會再呼叫API，額外重跑請另外記次數。
        沒有API時，先記離線功能與限制，真實語意欄寫「未測」；可引用教師實測紀錄，但要標明來源。

        | 評量 | 證據 |
        |---|---|
        | A功能與來源（40%） | 自我檢查、自己的邊界資料、原資料不被改寫 |
        | B比較與判讀（30%） | 三類問題、兩組參數、支持片段或不足理由；區分離線、自己API與教師紀錄 |
        | 錯誤修正（20%） | 一個錯誤或邊界、處理與重測 |
        | 可重現與反思（10%） | README含實際版本、模式、來源、限制與請求次數 |

        推送到整學期使用的Repo；老師從既有Google表單登記的Repo查看，不另交連結。ChromaDB／FAISS、RAG回答、File Search與部署都不列入本週基本作業。
    """)
    md("bridge", """
        ## 11. 下一週：把檢索接到RAG與File Search

        | 路線 | 第11週怎麼做 | 本週準備了什麼 |
        |---|---|---|
        | 自行建置 | 用本週的片段＋向量＋排名找證據 → 組成context → 模型回答並附來源 | rank_chunks與「回原文核對」的習慣 |
        | OpenAI File Search | 上傳支援格式的文件，由平台負責切塊、向量化、索引與檢索 | 知道平台做了哪些事，以及仍要自己核對原文 |

        本週用普通list看懂資料流；向量資料庫（如ChromaDB）的價值是管理大量向量與來源，細節留給自主選讀。
        兩條路線都要核對資料、證據與資訊不足的情況；第11週擇一實作即可。本週只有檢索，沒有產生回答，也沒有呼叫file_search。
        官方說明：[Embeddings](https://developers.openai.com/api/docs/guides/embeddings)｜[Retrieval](https://developers.openai.com/api/docs/guides/retrieval)｜[File Search](https://developers.openai.com/api/docs/guides/tools-file-search)
    """)
    md("checklist", """
        ## 12. 完成檢核

        - [ ] 能說明「意思相近→向量方向接近」，以及文件和問題要用同一個模型。
        - [ ] 能分清片段、向量、相似度、檢索與回答。
        - [ ] A只負責排名：來源保留、門檻與top_k正確，不在函式裡呼叫API。
        - [ ] 知道分數不是機率，也沒有通用門檻；離線規則找不到改寫題是規則限制。
        - [ ] 四種問題都有原文判讀，沒有證據不補造；教師紀錄有標明來源。
        - [ ] App改滑桿不新增API，失敗不留舊結果；README記了模式、版本與請求次數。
    """)
    return annotate_dependencies(cells, PREFIX, CELL_NOUNS, TAG_ALIASES)


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    (PACKAGE / "sample_data").mkdir(exist_ok=True)
    (PACKAGE / "sample_data/week09_cleaned_text.txt").write_text(DOC + "\n", encoding="utf-8")
    (PACKAGE / "sample_data/questions.json").write_text(
        json.dumps(QUESTIONS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for ending, teacher in [("學生版", False), ("教師版", True)]:
        cells = cells_for(teacher)
        for cell in cells:
            if cell["cell_type"] == "code":
                compile("".join(cell["source"]), cell["id"], "exec")
        book = {"cells": cells,
                "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                             "language_info": {"name": "python", "version": "3.14"}},
                "nbformat": 4, "nbformat_minor": 5}
        stem = WEEK / f"{TITLE}_{ending}"
        stem.with_suffix(".ipynb").write_text(json.dumps(book, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        reading = []
        for number, cell in enumerate(cells, 1):
            text = "".join(cell["source"])
            reading.append(f"<!-- 第{number}格 | {cell['id']} -->\n")
            reading.append(text if cell["cell_type"] == "markdown" else "```python\n" + text + "```\n")
        stem.with_suffix(".md").write_text("\n".join(reading), encoding="utf-8")

        folder = "teacher" if teacher else "student"
        target = PACKAGE / folder
        target.mkdir(exist_ok=True)
        header = block(f'''
            # 第10週片段搜尋・修訂版（{ending}）
            # 用途：文字→向量→A排名→回到原文確認；不產生回答。
            # 啟動：在week10/week10_semantic_search_revised執行
            # python -m streamlit run {folder}/app.py
            # 預設離線規則0次API；真實模式每次有效提交最多1次，滑桿重排0次。
            # 學生只補A；輸入、API與狀態完整提供，不另寫第二套App。
        ''')
        imports = ("import json\nimport math\nimport os\nfrom pathlib import Path\n\n"
                   "import streamlit as st\nfrom dotenv import load_dotenv\nfrom openai import OpenAI\n\n"
                   "# 金鑰：Cloud讀平台Secrets；本機讀.env或環境變數（見read_setting）。\n"
                   "# 先讀week10_semantic_search_revised/.env（Notebook也讀同一份），再讀入口資料夾的.env；已有的值不會被覆蓋。\n"
                   "load_dotenv(Path(__file__).resolve().parents[1] / '.env')\n"
                   "load_dotenv(Path(__file__).resolve().parent / '.env')\n"
                   "st.set_page_config(page_title='文件片段搜尋', layout='centered')\n")
        text = (header + "\n" + imports + "\n\n# ---------- 1. 完整提供的短函式與A練習 ----------\n"
                + READ_SETTING + "\n\n" + DEMO + "\n\n" + COSINE + "\n\n"
                + (RANK_TEACHER if teacher else RANK_STUDENT) + "\n\n" + APP)
        compile(text, str(target / "app.py"), "exec")
        (target / "app.py").write_text(text, encoding="utf-8")
        (target / ".streamlit").mkdir(exist_ok=True)
        (target / ".streamlit/secrets.example.toml").write_text(
            'OPENAI_API_KEY = "your_api_key_here"\nOPENAI_EMBEDDING_MODEL = "text-embedding-3-small"\n', encoding="utf-8")
        # Streamlit Cloud先找入口同層的requirements.txt，不會往上一層找
        (target / "requirements.txt").write_text(
            "streamlit==1.63.0\nopenai==2.49.0\npython-dotenv==1.2.3\n", encoding="utf-8")
    (PACKAGE / ".env.example").write_text(
        "OPENAI_API_KEY=your_api_key_here\nOPENAI_EMBEDDING_MODEL=text-embedding-3-small\n", encoding="utf-8")
    (PACKAGE / "requirements.txt").write_text(
        "# 課程固定直接依賴；Python3.14，目標環境需另行驗證。\nstreamlit==1.63.0\nopenai==2.49.0\npython-dotenv==1.2.3\n",
        encoding="utf-8")
    (PACKAGE / ".gitignore").write_text(".venv*/\n.env\n**/.streamlit/secrets.toml\n**/__pycache__/\n", encoding="utf-8")
    print("第10週修訂版重建完成：", len(cells), "格／版；雙版App與範例。")


if __name__ == "__main__":
    main()
