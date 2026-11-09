"""重建第10週課堂簡化版；原正式版與Claude參考均保留。"""
import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
WEEK = ROOT / "week10"
PACKAGE = WEEK / "week10_semantic_search_simple"
TITLE = "生成式AI應用開發_第10週_Embedding與語意搜尋_課堂簡化版"


def block(text):
    return dedent(text).strip() + "\n"


SAMPLE = (
    "文件處理工作坊於2026年11月11日14:00至16:00在圖書館討論室舉行。\n\n"
    "報名截止為2026年11月6日。報名方式尚未公告，請勿自行補造網址。\n\n"
    "本次名額32人，每組4人，共8組。文件沒有提供費用或餐點資訊。"
)
QUESTIONS = [
    {"query": "工作坊地點在哪裡？", "expected": "圖書館討論室"},
    {"query": "我要到哪裡參加這場活動？", "expected": "圖書館討論室"},
    {"query": "工作坊費用是多少？", "expected": "沒有提供費用"},
    {"query": "火星的平均氣溫是多少？", "expected": None},
]

DEMO = block('''
    # text：單段原文或單個查詢字串；每次只處理一筆。
    def demo_vector(text):
        """完整提供：人工指定4組關鍵字計數，不是模型學到的語意向量。"""
        groups = [
            ["地點", "圖書館", "哪裡"], ["報名", "截止"],
            ["名額", "人數", "幾人"], ["費用", "多少錢"],
        ]
        vector = []
        for words in groups:
            vector.append(float(sum(text.count(word) for word in words)))
        return vector
''')

COSINE = block('''
    # a、b：兩份非空、等長的有限數字清單；本週通常依序傳入片段向量與問題向量。
    def cosine_similarity(a, b):
        """完整提供：計算方向相似度；零向量回傳0，不能解讀為有語意證據。"""
        import math
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
    # chunks：帶 chunk_id、source、text 的片段字典清單；也可帶 start、end 等來源欄位。
    # vectors：文件向量清單；vectors[i] 必須來自 chunks[i]["text"]。
    # query_vector：一個問題的向量，與文件向量使用同一套轉換方式及相同維度。
    # top_k：最多回傳幾筆（正整數，預設 3）。min_score：保留分數的下限（預設 0.0，含等於）。
    def rank_chunks(chunks, vectors, query_vector, top_k=3, min_score=0.0):
        """傳入片段與同順序向量，回傳附score的來源資料；不呼叫API。"""
        if type(top_k) is not int or top_k <= 0:
            raise ValueError("top_k須為正整數")
        if not isinstance(min_score, (int, float)) or not -1 <= min_score <= 1:
            raise ValueError("min_score須介於-1與1")
        if len(chunks) != len(vectors):
            raise ValueError("片段與向量筆數不一致")
        if not chunks:
            return []
        # 完整提供：先確認向量可計算，零查詢向量不硬塞一筆結果。
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
                hit = dict(item)
                hit["score"] = score
                results.append(hit)
        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:top_k]
''')
RANK_STUDENT = block(RANK_COMMON + '''
        # TODO A：計算每筆score，保留>=min_score者；不可修改原chunks。
        # 用dict(item)複製來源，加入score；由高至低排序，回傳前top_k筆。
        raise NotImplementedError("請完成TODO A：來源保留、篩選與排序")
''')

DATA = block('''
    # 用途：第9週已核對的短片段；每段作一個單位，0次API。
    chunks = [
        {"chunk_id": 0, "source": "活動說明.txt", "text": "工作坊在圖書館討論室舉行。"},
        {"chunk_id": 1, "source": "活動說明.txt", "text": "報名截止為11月6日，報名方式未公告。"},
        {"chunk_id": 2, "source": "活動說明.txt", "text": "本次名額32人，每組4人；沒有提供費用。"},
    ]
''')

A_CHECK = block('''
    # 用途：固定資料自測 A，0 次 API。
    # 需要：先執行第 4-1 節的 cosine_similarity，再執行第 5 節的 rank_chunks 定義格。
    # 學生版完成或修改 TODO A 後，請重跑 rank_chunks 定義格再自測。
    hits_result = None
    try:
        check_chunks = [
            {"chunk_id": 10, "source": "測試.txt", "text": "第一段"},
            {"chunk_id": 11, "source": "測試.txt", "text": "第二段"},
            {"chunk_id": 12, "source": "測試.txt", "text": "第三段"},
        ]
        check_vectors = [[0.0, 1.0], [1.0, 0.0], [0.8, 0.6]]
        # 前三個引數依序是測試片段、片段向量、問題向量；2 是筆數上限，0.5 是最低分數。
        hits_result = rank_chunks(check_chunks, check_vectors, [1.0, 0.0], 2, 0.5)
        assert [item["chunk_id"] for item in hits_result] == [11, 12]
        assert all(item["source"] == "測試.txt" for item in hits_result)
        assert "score" not in check_chunks[0]
        assert rank_chunks(check_chunks, check_vectors, [0.0, 0.0]) == []
        print("A通過：排序、門檻、top_k、來源與不修改原文")
    except NotImplementedError as exc:
        print(exc)
''')

REAL = block('''
    # 用途：同一模型一次向量化3段文件與3個問題；本格獨立，0或1次API。
    # 操作：完成API設定後才改True；全部執行時預設略過，重跑另計。
    import os
    import sys
    import math
    RUN_REAL_EMBEDDINGS = False
    embedding_result = None
    embedding_error = None
    documents = ["工作坊在圖書館討論室舉行。", "報名截止11月6日。", "名額32人，沒有提供費用。"]
    questions = ["地點在哪裡？", "我要到哪裡參加？", "火星的平均氣溫是多少？"]
    if RUN_REAL_EMBEDDINGS:
        try:
            from openai import OpenAI
            from dotenv import load_dotenv
            load_dotenv()
            key = os.getenv("OPENAI_API_KEY", "")
            if "google.colab" in sys.modules:
                from google.colab import userdata
                key = userdata.get("OPENAI_API_KEY")
            if not key:
                raise ValueError("請先設定並授權OPENAI_API_KEY")
            model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
            inputs = documents + questions
            # api_key 提供認證；max_retries=0 關閉 SDK 自動重試；timeout=60.0 設定網路逾時秒數。
            # model 選向量模型；input 傳整批文字；encoding_format="float" 要求數字清單。
            with OpenAI(api_key=key, max_retries=0, timeout=60.0) as client:
                response = client.embeddings.create(model=model, input=inputs, encoding_format="float")
            ordered = sorted(response.data, key=lambda item: item.index)
            if [item.index for item in ordered] != list(range(len(inputs))):
                raise ValueError("回傳向量筆數或順序不合格")
            vectors = [item.embedding for item in ordered]
            for vector in vectors:
                if not vector or len(vector) != len(vectors[0]):
                    raise ValueError("向量為空或維度不一致")
                if not all(type(x) in (int, float) and math.isfinite(x) for x in vector) or not any(vector):
                    raise ValueError("向量含非有限數字或全零")
            embedding_result = {"model": model, "documents": documents, "questions": questions, "vectors": vectors}
        except Exception as exc:
            embedding_error = "本次未保存向量，錯誤類型：" + type(exc).__name__
    print("已保存真實向量" if embedding_result else embedding_error or "已略過API；尚未取得真實語意向量")
''')

READ_SETTING = block('''
    # name 是設定名稱；找不到該設定時回傳 default，省略時用空字串。
    def read_setting(name, default=""):
        """完整提供：平台Secrets優先，本機使用環境變數或App旁.env。"""
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
    st.caption("預設為離線關鍵字規則向量，不能當成語意搜尋證據。真實模式每次有效提交最多1次API。")
    st.session_state.setdefault("record", None)
    st.session_state.setdefault("error", "")
    if st.session_state.get("real_api_mode") != real_api:
        st.session_state.record = None
        st.session_state.error = ""
        st.session_state.real_api_mode = real_api
    if st.button("清除結果"):
        st.session_state.record = None
        st.session_state.error = ""

    # ---------- 3. 表單收集已核對的文字與問題 ----------
    # 一個空白行分一段；直接使用第9週確認過的文字，不再寫PDF／Word reader。
    sample = (Path(__file__).resolve().parents[1] / "sample_data/activities.txt").read_text(encoding="utf-8")
    with st.form("search_form"):
        source = st.text_area("文件文字（空白行分段）", value=sample, height=210)
        query = st.text_input("查詢問題", value="工作坊地點在哪裡？")
        submitted = st.form_submit_button("建立向量並搜尋")

    if submitted:
        st.session_state.record = None  # 新提交失敗不能沿用舊成功資料。
        st.session_state.error = ""
        try:
            # ---------- 4. 輸入與單位：全在本機檢查 ----------
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
                    start = source.find(text, cursor)
                    end = start + len(text)
                    chunks.append({
                        "chunk_id": len(chunks), "source": "貼入文字",
                        "start": start, "end": end, "text": text,
                    })
                    cursor = end
            if len(chunks) > 12:
                raise ValueError("最多12段，請縮小教學文件範圍")
            # 未完成A先在本機提示；不因按下按鈕而浪費API請求。
            rank_chunks([{"chunk_id": 0, "source": "檢查", "text": "檢查"}], [[1.0]], [1.0])
            inputs = [item["text"] for item in chunks] + [query]

            # ---------- 5. 取得同一向量空間的文件與問題向量 ----------
            if real_api:
                key = read_setting("OPENAI_API_KEY")
                if not key:
                    raise ValueError("缺少OPENAI_API_KEY，請設定.env或平台Secrets")
                model = read_setting("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
                # 小型教學批次：文件＋問題合併為1次；每次新提交會重新向量化。
                # 正式服務應保存文件向量，後續只向量化新問題；本例不做跨次快取。
                # api_key 提供認證；max_retries=0 關閉 SDK 自動重試；timeout=60.0 設定網路逾時秒數。
                # model 選向量模型；input 傳整批文字；encoding_format="float" 要求數字清單。
                with OpenAI(api_key=key, max_retries=0, timeout=60.0) as client:
                    response = client.embeddings.create(
                        model=model, input=inputs, encoding_format="float",
                    )
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
            # 不混用兩種向量；保存本次原文、模型與同批向量，供本機重排。
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

    # ---------- 6. 只在本機改排名：不再次呼叫API ----------
    # 滑桿依序接收標籤、最小值、最大值、初始值、步長。整數滑桿省略步長時每次加減 1。
    top_k = st.slider("最多顯示幾段（top_k）", 1, 5, 2)
    min_score = st.slider("最低分數（不是正確機率）", 0.0, 1.0, 0.0, 0.05)
    if st.session_state.error:
        st.error(st.session_state.error)
    if st.session_state.record is not None:
        record = st.session_state.record
        try:
            # 建立批次時把問題放最後，所以 [:-1] 是全部文件向量，[-1] 是問題向量。
            hits = rank_chunks(
                record["chunks"], record["vectors"][:-1],
                record["vectors"][-1], top_k, min_score,
            )
            st.caption("以下為上次成功提交；修改表單尚未提交時，不會更新原文或問題。")
            st.write("模式：", record["mode"], "模型：", record["model"])
            st.write("本次問題：", record["query"])
            if not hits:
                st.warning("沒有可用片段；請檢查關鍵字規則、門檻與原文，不能補造答案。")
            for item in hits:
                st.write(f"chunk {item['chunk_id']}｜分數 {item['score']:.4f}｜來源 {item['source']}｜{item['start']}:{item['end']}")
                st.write(item["text"])
            with st.expander("核對本次原文"):
                st.text(record["source"])
            # 只匯出原文與來源結果；不把金鑰或整批高維向量寫入檔案。
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


def cells_for(teacher):
    cells = []

    def add(kind, tag, text, requires=()):
        cell = {"cell_type": kind, "id": "w10s-" + tag, "metadata": {"teaching": {"requires": list(requires)}}, "source": block(text).splitlines(keepends=True)}
        if kind == "code":
            cell.update(execution_count=None, outputs=[])
        cells.append(cell)

    def md(tag, text):
        add("markdown", tag, text)

    def code(tag, text, requires=()):
        add("code", tag, text, requires)

    edition = "教師版" if teacher else "學生版"
    md("cover", f"""
        # 第10週｜Embedding與語意搜尋・課堂簡化版（{edition}）

        主線：**已核對片段 → 向量 → 相似度 → 相關片段 → 原文證據**。
        第9週處理資料品質，本週只找資料，第11週才依證據生成回答。
        <font color="#C62828"><b>重要：</b></font>相似度不是答案正確機率；找得到一段，也不代表它能回答問題。
        原教材保留；配套App見[README](week10_semantic_search_simple/README.md)。
    """)
    md("goals", """
        ## 0. 先備、學習目標與150分鐘

        先備：第2週list/dict、函式、sorted與lambda；第7週表單與session_state；第9週片段與來源回查。
        不需先學NumPy矩陣、ChromaDB／FAISS安裝或再寫一套PDF／Word reader。

        | 時間 | 核心活動 |
        |---|---|
        | 15分鐘 | 第9～11週地圖與Embedding用途 |
        | 20分鐘 | 片段、問題與手寫小向量 |
        | 20分鐘 | 完整cosine示範與分數判讀 |
        | 25分鐘 | A完成來源保留、門檻與排序，自測修正 |
        | 25分鐘 | 真實API批次示範與B三種問題觀察 |
        | 30分鐘 | 移入A到同一App、改參數與來源核對 |
        | 15分鐘 | 互看、錯誤與作業說明 |

        共150分鐘，另休息10與排障20分鐘。必做A與B；只做一個App。
        無API時先做離線功能驗證，B的真語意觀察留待教師示範或課前安排；不能填假模型結果。
    """)
    md("setup", """
        ## 1. 環境與費用界線

        Notebook讀概念與短例；Streamlit在本機VS Code啟動。新版沿用Windows／Python3.14課程環境，Colab版本由平台管理。
        核心數學與排序只用內建模組；App需要Streamlit、OpenAI與python-dotenv，不增加向量資料庫依賴。
        本機金鑰放環境變數或自己的.env；Colab在Secrets設定OPENAI_API_KEY並授權Notebook，重啟後重跑必要定義格。
        真實活動開關放使用格，預設False。Notebook固定3段＋3問題合併1次請求；App每次有效新提交1次，重測另計。
        真實模式仍傳送文件與問題，禁止個資、機密與未授權資料。60秒是網路等待，不保證整個任務60秒內結束。
    """)
    code("install", """
        # 用途：顯示環境；僅需要API／App時才安裝，0次API。
        # Colab取消下行註解；本機依配套README使用python -m pip。
        # %pip install openai==2.49.0 python-dotenv==1.2.3
        import sys
        print("Python：", sys.version)
    """)
    md("units", """
        ## 2. 從第9週接入：片段與來源

        每個片段要保留text與可回查來源。下格自帶3段，不依賴第9週TODO或檔案，獨立、0次API。
        短段落、FAQ或CSV一整列都可作為單位；不必為每份資料重寫固定字元切塊。
        本週App直接貼第9週已確認的文字，以空白行分段；沒有自動匯入第9週JSON，不把檔案下載誤認為搜尋完成。
    """)
    code("data", DATA)
    md("embedding", """
        ## 3. Embedding：把文字變成可比較的數字

        模型將文字轉成高維數字清單；文件和問題必須使用相同模型與維度，才可比較。
        Embeddings API只回傳向量，不會自動建立資料庫、找來源或生成回答。
        下格人工指定2維向量，只教方向比較，不能宣稱它是OpenAI模型輸出；實際向量每一維也沒有固定可讀的詞義。
    """)
    code("small-vector", """
        # 用途：手寫向量的方向，不呼叫模型；可獨立執行。
        query_vector = [1.0, 0.0]
        doc_a = [1.0, 0.0]
        doc_b = [0.0, 1.0]
        print("問題方向：", query_vector, "A：", doc_a, "B：", doc_b)
        # 本格只準備數字，下節再用公式比較；沒有語意搜尋證據。
    """)
    md("cosine", """
        ## 4. Cosine：比較方向，不能當作正確率

        cosine是內積除以兩個長度的乘積，範圍約-1到1。同方向接近1，正交是0。
        這裡不是機率；0.8不能解讀成「答案80%正確」，也沒有所有資料都適用的固定門檻。
        下格完整提供，函式內自帶math；zip逐對取值、sum加總、sqrt求長度。先驗維度與有限數字，零向量回傳0。
    """)
    md("syntax", """
        ### 4-1 讀程式需要的短語法

        在 cosine_similarity(a, b) 中，a、b 是要比較的兩個數字清單，兩者都必填且維度相同。
        搜尋時通常把片段向量放 a，問題向量放 b；互換順序會得到相同的 cosine。
        例如 cosine_similarity([1.0, 0.0], [2.0, 0.0]) 會回傳 1.0，因為兩個向量方向相同。

        下格cosine的zip(a,b)把兩份向量逐對取值；前面的長度檢查避免不同維度被zip悄悄截短。
        sum(x*y for x,y in zip(a,b))把每對乘積加總；這裡括號內是逐一產生數字，不需先建立完整清單。
        all(...)要求每項都通過，math.isfinite排除NaN／無限值；any(vector)判斷是否至少一個分量非零。
        A的dict(item)複製單層來源資料，再加score，避免改到原chunks；results[:top_k]取前k筆，不會補足缺少的筆數。
        看不熟時回下格對照；無須另寫通用驗證框架或背誦公式推導。
    """)
    code("cosine-fn", COSINE)
    code("cosine-example", """
        # 用途：以本格的手寫向量驗證 cosine，0 次 API。
        # 需要：先執行第 4-1 節定義 cosine_similarity 的程式碼格。
        print(cosine_similarity([1.0, 0.0], [2.0, 0.0]))
        print(cosine_similarity([1.0, 0.0], [0.0, 1.0]))
        print(cosine_similarity([0.0, 0.0], [1.0, 0.0]))
        # 預期1、0、0；零向量的0是無有效方向，不代表文件語意已被理解。
    """, ["cosine-fn"])
    md("ranking", """
        ## 5. A：把分數變成可回查的結果（必做，約20分鐘含修正）

        先跑 cosine，再定義 A。前三個參數必填，後兩個可省略；回傳附來源及分數的片段清單。

        | 參數 | 傳入什麼 | 作用 |
        |---|---|---|
        | `chunks` | 字典清單。每筆含 `chunk_id`、`source`、`text`，也可帶位置欄位 | 保留片段原文與來源供回查 |
        | `vectors` | 文件向量清單，筆數與 `chunks` 相同 | `vectors[i]` 必須由 `chunks[i]["text"]` 轉成；順序錯了會把分數配到別段 |
        | `query_vector` | 單一問題的數字向量 | 與每段文件向量比較；模型或離線規則必須相同，維度也要相同 |
        | `top_k=3` | 正整數 | 限制最多回傳幾段；合格片段較少時就只回傳那些片段 |
        | `min_score=0.0` | −1 到 1 的分數 | 先排除低於門檻的片段；分數剛好等於門檻也保留 |

        下方自測的位置引數 `2, 0.5` 等同於寫 `top_k=2, min_score=0.5`。假設分數是 0.9、0.4、0.2，門檻 0.5 只留下 0.9，因此最多可取 2 段、實際只回傳 1 段。
        已提供筆數、維度、參數檢查與零查詢處理；學生只補計分、來源複製、篩選、排序與取前k筆。
        每筆保留原來源欄位並新增score；不可修改原chunks。原始分數>=min_score才保留，先篩再排序，最後切片。
        沒有合格片段回傳[]；不能只print。下個固定檢查格保存hits_result，App沿用同一函式。
        sorted或list.sort都可；key=lambda item:item['score']指定依分數排，reverse=True由高到低。這是第2週語法回查。
    """)
    code("a", block("""
        # 需要：呼叫 rank_chunks 前，先執行第 4-1 節定義 cosine_similarity 的程式碼格。
    """) + (RANK_TEACHER if teacher else RANK_STUDENT), ["cosine-fn"])
    code("a-check", A_CHECK, ["cosine-fn", "a"])
    md("a-result", """
        A應通過排序與來源檢查。若結果反向，查reverse；原文被改，查是否直接在原dict寫score；筆數不對，查篩選與切片。
        請保留一次失敗→修正→重測，或另設一筆空結果邊界。通過自測只證明功能，不代表真語意品質。
    """)
    md("offline", """
        ## 6. 離線流程示範：人工關鍵字規則向量

        下格完整提供4組人工關鍵字計數，只為無金鑰時驗證資料流與排序；不是訓練模型、不是語意Embedding。
        demo_vector(text) 的 text 是一段原文或一個問題字串，回傳依固定組別順序排列的 4 個計數。
        例如 demo_vector("圖書館在哪裡？") 會得到 [2.0, 0.0, 0.0, 0.0]，因為「圖書館」與「哪裡」都在第一組。
        「地點」「哪裡」因人工放同組才接近；換句話若沒中規則可能全零。不能用離線排名證明模型懂同義句。
        離線與真實向量不可混用，分數也不可跨模式直接比較。
    """)
    code("demo-fn", DEMO)
    code("offline-run", block("""
        # 需要：先執行第 4-1 節的 cosine_similarity、第 5 節的 rank_chunks，
        # 以及第 6 節的 demo_vector 定義格。學生版須完成 TODO A 並重跑定義格。
    """) + DATA + "\n" + block('''
        # 用途：以 A 串接人工規則，0 次 API。
        offline_hits = None
        try:
            vectors = [demo_vector(item["text"]) for item in chunks]
            query_vector = demo_vector("地點在哪裡？")
            offline_hits = rank_chunks(chunks, vectors, query_vector, top_k=2, min_score=0.1)
            print("離線規則結果（非語意證據）：", offline_hits)
        except NotImplementedError as exc:
            print(exc)
    '''), ["cosine-fn", "a", "demo-fn"])
    md("real", """
        ## 7. 真實Embeddings API：同批文件與問題

        下格自帶文件與問題，可獨立執行；預設False為0次。改True有效執行1次請求，包含3段文件與3個問題，沒有回答生成API。
        | 呼叫 | 參數 | 本例代表的意思 |
        |---|---|---|
        | `OpenAI(...)` | `api_key=key` | 用本機環境或 Colab Secrets 讀到的金鑰認證 |
        | `OpenAI(...)` | `max_retries=0` | SDK 失敗後不自動重送；第一次請求仍會送出 |
        | `OpenAI(...)` | `timeout=60.0` | 以秒設定 SDK 的網路逾時 |
        | `client.embeddings.create(...)` | `model=model` | 指定產生向量的模型；本例從設定讀取，未設定時用 `text-embedding-3-small` |
        | `client.embeddings.create(...)` | `input=inputs` | 傳入 `documents + questions`，前三筆是文件，後三筆是問題 |
        | `client.embeddings.create(...)` | `encoding_format="float"` | 回傳每筆向量的浮點數清單，方便直接計算 cosine |

        在 `model=model` 中，左側是 API 的參數名稱，右側是本格已設定的變數。
        `sorted(response.data, key=lambda item: item.index)` 的第一個引數是要排序的回應資料，`key` 指定用輸入位置 `index` 排序。對齊後再取各筆的 `embedding`。
        文件與問題使用同一模型。檢查筆數、順序、維度、有限數字與非零後，才保存embedding_result；失敗先清舊資料。
        資料很小，這格合批避免多次請求；實務索引可保存文件向量，新問題只算新問題，不需每次重算文件。
        官方依據：[Embeddings](https://developers.openai.com/api/docs/guides/embeddings)。
    """)
    code("real-run", REAL)
    md("real-result", """
        ### 7-1 觀察三個問題的排名

        需cosine、A與上一格結果。沒執行真實API只提示未測，不用人工規則冒充。
        假設 count=3，vectors[:count] 取索引 0、1、2 的文件向量。offset 是目前問題在問題清單中的索引，從 0 起算；vectors[count + offset] 因此取到對應的單一問題向量。
        用同一批文件與問題做B：原句、換句話、文件外問題。先記預期證據，再看排名；沒有固定分數或必然正確順序。
        文件外問題仍可能有最高分，必須回原文判斷「找到了字串」是否真的支持問題。
    """)
    code("real-rank", """
        # 用途：重用已保存向量做排名，0 次新 API。
        # 需要：先執行第 4-1 節的 cosine_similarity，再執行第 5 節的 rank_chunks 定義格。
        # 再執行第 7 節產生 embedding_result 的程式碼格。API 關閉或執行失敗時，本格會提示未測。
        real_rankings = None
        if embedding_result is None:
            print("尚未取得真實向量，B的真語意觀察未測")
        else:
            try:
                count = len(embedding_result["documents"])
                real_chunks = []
                for index, text in enumerate(embedding_result["documents"]):
                    real_chunks.append({"chunk_id": index, "source": "固定活動說明", "text": text})
                real_rankings = []
                for offset, question in enumerate(embedding_result["questions"]):
                    hits = rank_chunks(
                        real_chunks,
                        embedding_result["vectors"][:count],  # 文件向量，順序對應 real_chunks
                        embedding_result["vectors"][count + offset],  # 目前這一題的向量
                        2, 0.0,  # top_k 與 min_score
                    )
                    real_rankings.append({"query": question, "hits": hits})
                    print(question, hits)
            except NotImplementedError as exc:
                print(exc)
    """, ["cosine-fn", "a", "real-run"])
    md("b", """
        ## 8. B：同資料、三種問題與兩組篩選（必做觀察）

        TODO B：沿用同一資料，不再寫第二個搜尋器；在紀錄表填實際問題、預期來源、top_k、min_score、前幾名與證據。
        1. 原句問題、同義改寫、文件外問題各一題；指出支持答案的chunk_id與原文，沒有證據就寫不足。
        2. 固定一個問題與向量，只改top_k=1與2，或固定k只改兩個門檻；一次只變一項，回查增加／消失的片段。
        3. 記一次錯誤或邊界與處理，如空問題、規則全零、門檻排光或API失敗，不能補造模型結果。
        Notebook可重用embedding_result保存的向量，App滑桿在本機重排，均不新增API；改文字／新問題提交才另計。
        沒有API權限時可先交離線功能與規則限制紀錄；真語意欄寫未測，教師另安排共看真實示範，不以假結果補齊。
    """)
    md("b-reference", """
        ### 8-1 B紀錄與判讀

        | 模式／模型 | 問題／預期來源 | k／門檻 | 實際chunk_id與分數 | 原文是否支持／限制 |
        |---|---|---|---|---|
        | 自己填 | 自己填 | 自己填 | 實際執行後填 | 自己判讀 |

        得分高卻無原文支持，要記錄為檢索不足，不能直接生成肯定答案。查不到費用與文件外問題也要分清楚：前者有「未提供」的原文，後者整份文件不談該主題。
    """)
    if teacher:
        cells[-1]["source"] += ["\n"] + block("""
            教師提醒：真實排名須課前實跑再填；不得在學生版預填保證順序。離線同義句可能全零，這是人工規則限制。
            優先檢查原文支持與比較條件，不按最高分數加分。資訊不足的合理結論也是有效成果。
        """).splitlines(keepends=True)
    md("app", """
        ## 9. 把A移入同一個Streamlit App

        配套student/app.py只有A待完成；把已驗收的rank_chunks貼入對應位置。cosine、離線規則與UI完整提供，不重寫reader。
        文件直接貼第9週核對後文字，以空白行分成最多12段；保留start/end可回查貼入文字。這不是自動匯入第9週JSON。
        預設離線0次；勾真實模式有效提交最多1次，合批文件與問題。每次新提交都重算；改top_k／門檻只在本機重排，0次新請求。
        App 的滑桿先給標籤，再給最小值、最大值、初始值與步長。top_k 可選 1 到 5、初始為 2；min_score 可選 0.0 到 1.0、初始為 0.0、每格 0.05。滑桿值會傳給 rank_chunks，取代函式簽名中的預設值。
        表單未提交改值時顯示上次成功資料；切模式、清除或新提交失敗清舊結果。先完成A再允許付費請求。
        保存模式、模型、原文、問題與向量；下載只放來源結果，不輸出金鑰或整批向量。這是小文件教學App，不是正式大型索引。
    """)
    md("homework", """
        ## 10. 回家作業：同一App的搜尋證據（45～60分鐘）

        沿用A與同一App，換一份合法無敏感資料的小文件或自寫3～6段虛構內容，保留原文件／貼入文字。最低要求固定、題目自由。
        交學生Notebook（A自測＋B紀錄）、同一App、文件與README，另附兩組參數的搜尋紀錄JSON，不做第二個作品。
        README記原句／改寫／文件外三種問題；至少一題有支持來源，一題指出證據不足。固定同一題比較兩組k或門檻並說理由。
        同時記一個錯誤／邊界的預期、實際、修正與重測，人工核對一個日期或數字。截圖或文字證據擇一，不重複堆疊。
        正常規畫：Notebook教師合批示範1次；學生App三種新問題各1次，共3次。滑桿比較與下載0次，額外重跑另計。
        沒有真實API者先記離線功能與限制，真語意欄明寫未測；不得以離線分數當模型品質。教師安排的真實共看另記模式與實際結果。

        | 評量 | 證據 |
        |---|---|
        | A功能與來源（40%） | 固定自測、自己的邊界、原資料不被改寫 |
        | B比較與判讀（30%） | 三類問題、兩組參數、支持片段或不足理由；區分離線與真實 |
        | 錯誤修正（20%） | 一個錯誤／邊界、處理與重測 |
        | 可重現與反思（10%） | README含實際版本、模式、來源、限制與請求數 |

        沿用整學期Repo及既有Google表單登記，Commit／Push後到GitHub確認，不另交每週資料夾連結。
        ChromaDB／FAISS、RAG回答、File Search、部署均不列本週基本作業，不為多功能加重負擔。
    """)
    md("bridge", """
        ## 11. 下一週：把檢索接到RAG與File Search

        自行建置路線：本週片段＋向量＋搜尋 → 第11週組context → 模型回答與來源核對。
        File Search路線：上傳支援文件，由平台處理切塊／向量／索引／檢索，再供模型使用；不是每個App都要自己寫資料庫與切塊。
        本週用普通list看懂資料流，向量資料庫的價值是管理大量向量、來源與搜尋；ChromaDB細節留後續，自主選讀不占核心。
        兩條路線都需核對資料、證據與不足情境；後續專題擇一，不要求兩套。本週只有retrieval，沒有Responses生成或file_search請求。
        [Embedding官方說明](https://developers.openai.com/api/docs/guides/embeddings)｜[Retrieval](https://developers.openai.com/api/docs/guides/retrieval)｜[File Search](https://developers.openai.com/api/docs/guides/tools-file-search)
    """)
    md("checklist", """
        ## 12. 完成檢核

        - [ ] 能分清片段、向量、相似度、檢索與回答。
        - [ ] A只負責排名，來源保留、門檻與top_k正確；不在函式呼叫API。
        - [ ] 知道相同模型／維度才能比較；分數不是機率，也不是通用門檻。
        - [ ] 三類問題有原文判讀，無證據不補造；離線規則不冒充真語意。
        - [ ] App改滑桿不新增API，失敗不留下舊成果；已記模式、版本與請求數。
    """)
    return cells


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    (PACKAGE / "sample_data").mkdir(exist_ok=True)
    (PACKAGE / "sample_data/activities.txt").write_text(SAMPLE + "\n", encoding="utf-8")
    (PACKAGE / "sample_data/questions.json").write_text(json.dumps(QUESTIONS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for ending, teacher in [("學生版", False), ("教師版", True)]:
        cells = cells_for(teacher)
        book = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3.14"}}, "nbformat": 4, "nbformat_minor": 5}
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
            # 第10週片段搜尋・課堂簡化版（{ending}）
            # 用途：文字→向量→A排名→來源；不生成回答。
            # 啟動：在week10/week10_semantic_search_simple執行
            # python -m streamlit run {folder}/app.py
            # 預設離線規則0次API；真實模式有效新提交最多1次，滑桿重排0次。
            # 學生只補A；輸入、API與狀態完整提供，不另寫第二套App。
        ''')
        imports = "import json\nimport math\nimport os\nfrom pathlib import Path\n\nimport streamlit as st\nfrom dotenv import load_dotenv\nfrom openai import OpenAI\n\nload_dotenv(Path(__file__).resolve().parent / '.env')\nst.set_page_config(page_title='文件片段搜尋', layout='centered')\n"
        text = header + "\n" + imports + "\n# ---------- 1. 完整提供的短函式與A練習 ----------\n" + READ_SETTING + "\n" + DEMO + "\n" + COSINE + "\n" + (RANK_TEACHER if teacher else RANK_STUDENT) + "\n" + APP
        (target / "app.py").write_text(text, encoding="utf-8")
        (target / ".streamlit").mkdir(exist_ok=True)
        (target / ".env.example").write_text("OPENAI_API_KEY=your_api_key_here\nOPENAI_EMBEDDING_MODEL=text-embedding-3-small\n", encoding="utf-8")
        (target / ".streamlit/secrets.example.toml").write_text('OPENAI_API_KEY = "your_api_key_here"\nOPENAI_EMBEDDING_MODEL = "text-embedding-3-small"\n', encoding="utf-8")
        (target / ".gitignore").write_text(".env\n.streamlit/secrets.toml\n.venv*/\n__pycache__/\n", encoding="utf-8")
    (PACKAGE / "requirements.txt").write_text("# 課程固定直接依賴；Python3.14，目標環境需另行驗證。\nstreamlit==1.63.0\nopenai==2.49.0\npython-dotenv==1.2.3\n", encoding="utf-8")
    (PACKAGE / ".gitignore").write_text(".venv*/\n**/.env\n**/.streamlit/secrets.toml\n**/__pycache__/\n", encoding="utf-8")
    print("第10週課堂簡化版重建完成：", len(cells), "格／版；雙版App與範例。")


if __name__ == "__main__":
    main()
