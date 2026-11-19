# ---------- 3. 整合時新增的短函式：明確保留每一步資料 ----------
def prepare_document(filename, data, encoding, chunk_size, overlap, by_paragraph=False):
    """接收檔名、bytes、文字編碼與切塊設定，回傳原文、清理文字及來源片段。

    by_paragraph=True：用第10、11週的split_chunks，一個空白行一段；chunk_size與overlap不使用。
    by_paragraph=False：用第9週的chunk_text；chunk_size是每段最多字元數，overlap是相鄰片段重複字元數。
    start/end指向cleaned_text，end不包含；不代表原PDF的字元位置。
    """
    if not data or len(data) > 1024 * 1024:
        raise ValueError("請使用非空且不超過1MB的文件。")
    raw_text = extract_text(filename, data, encoding)
    cleaned_text = clean_text(raw_text)
    if not cleaned_text or len(cleaned_text) > 20000:
        raise ValueError("清理後須有1～20000字元；請檢查內容或縮小文件。")
    if by_paragraph:
        chunks = split_chunks(cleaned_text, filename)
        if any(len(item["text"]) > 1000 for item in chunks):
            raise ValueError("有段落超過1000字元；請改用「固定字元」切塊。")
        chunk_size, overlap = None, None
    else:
        chunks = chunk_text(cleaned_text, chunk_size, overlap)
    if not chunks or len(chunks) > 100:
        raise ValueError("文件須切成1～100段；請增加片段長度或縮小文件。")
    for item in chunks:
        item["source"] = filename
    return {"filename": filename, "file_sha256": sha256(data).hexdigest(),
            "byte_size": len(data), "encoding": encoding,
            "split": "空白行分段" if by_paragraph else "固定字元", "chunk_size": chunk_size,
            "overlap": overlap, "raw_text": raw_text, "cleaned_text": cleaned_text, "chunks": chunks}


def embed_texts_checked(client, model, texts):
    """以同一model合批嵌入texts；依API index還原順序，回傳對齊的向量清單。"""
    response = client.embeddings.create(model=model, input=texts, encoding_format="float")
    items = sorted(response.data, key=lambda item: item.index)
    if [item.index for item in items] != list(range(len(texts))):
        raise ValueError("向量回傳筆數或索引不一致，請重新建立。")
    vectors = [item.embedding for item in items]
    dimension = len(vectors[0]) if vectors else 0
    for vector in vectors:
        if not dimension or len(vector) != dimension or not any(vector):
            raise ValueError("向量維度不一致或向量為空，請重新建立。")
        cosine_similarity(vector, vector)  # 沿用第10週有限數字檢查。
    return vectors


def retrieve_evidence(document, index, question, query_vector, top_k, min_score, max_chars):
    """保留全段排名、入選hits與真正放入context的sources；三者不可混為一談。"""
    chunks, vectors = document["chunks"], index["vectors"]
    ranking = rank_chunks(chunks, vectors, query_vector, len(chunks), -1.0)
    hits = rank_chunks(chunks, vectors, query_vector, top_k, min_score)
    pack = build_context(hits, max_chars=max_chars)
    return {"mode": index["mode"], "embedding_model": index["model"], "question": question,
            "query_vector": query_vector, "top_k": top_k, "min_score": min_score,
            "max_chars": max_chars, "ranking": ranking, "hits": hits,
            "sources": pack["sources"], "context": pack["text"],
            "input": build_input(question, pack["text"]) if pack["sources"] else ""}


def generate_answer(client, model, evidence):
    """只送已預覽的context；沒有sources不送請求，只有完整非空回答才回傳。"""
    if not evidence["sources"]:
        return INSUFFICIENT
    response = client.responses.create(
        model=model, instructions=INSTRUCTIONS, input=evidence["input"], store=False,
    )
    refused = any(getattr(part, "type", "") == "refusal"
                  for item in response.output for part in getattr(item, "content", []))
    if response.status != "completed" or refused or not response.output_text.strip():
        raise ValueError("模型未完成、拒絕回答或回傳空白；本次不保存答案。")
    return response.output_text.strip()


def open_client():
    """平台Secrets優先，再讀已載入的.env／環境變數；不讓SDK自動重試。"""
    key = read_setting("OPENAI_API_KEY")
    if not key:
        raise ValueError("缺少OPENAI_API_KEY：本機請設定.env，Cloud請設定Secrets。")
    return OpenAI(api_key=key, max_retries=0, timeout=60.0)


def show_failure(exc):
    """API錯誤只顯示類型與狀態碼，不把可能含私人資料的原始回應印出來。"""
    if isinstance(exc, UnicodeDecodeError):
        message = "文字編碼不符，請改選UTF-8或cp950後重試。"
    elif isinstance(exc, ValueError):
        message = str(exc)
    else:
        status = getattr(exc, "status_code", None)
        message = f"本次處理失敗（{type(exc).__name__}"
        message += f"，狀態碼{status}" if status else ""
        message += "），請檢查文件、金鑰、模型權限或連線後重試。"
    st.error(message)


def make_record(document, index, evidence, answer, model, attempts):
    """保存來源與操作設定，保留原第11週讀回格需要的hits/context；不存金鑰或向量。"""
    check, labels = check_answer(answer, evidence["sources"])
    return {"record_version": 1, "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "mode": evidence["mode"], "embedding_model": index["model"],
            "answer_model": model if evidence["sources"] else None,
            "document": document, "question": evidence["question"],
            "top_k": evidence["top_k"], "min_score": evidence["min_score"],
            "max_chars": evidence["max_chars"], "ranking": evidence["ranking"],
            "hits": evidence["hits"], "sources": evidence["sources"],
            "context": evidence["context"], "instructions": INSTRUCTIONS,
            "input": evidence["input"], "answer": answer, "check": check,
            "used_labels": labels, "api_attempts_session": dict(attempts)}


# ---------- 4. 目前使用者的狀態；不以全域快取共用上傳文件 ----------
for name in ("document", "index", "query_cache", "evidence", "record"):
    st.session_state.setdefault(name, None)
st.session_state.setdefault("api_attempts", {"文件向量": 0, "問題向量": 0, "回答": 0})

st.title("看得見每一步的RAG文件問答")
st.caption("第9週讀檔與前處理 → 第10週向量與搜尋 → 第11週依證據回答與回查。")
st.info("先準備文件，再提問找證據，最後依證據回答。預設離線，所有付費操作都要另按按鈕。")

with st.sidebar:
    st.subheader("執行模式")
    real_api = st.checkbox("使用真實API（可能產生費用）", value=False, key="real_api")
    st.caption("離線向量只是四組活動關鍵字計數，不是語意Embedding；離線不產生模型答案。")
    st.caption("真實模式會將文件片段送到Embedding API，再將問題與入選證據送到回答API。")
    embed_model = read_setting("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    answer_model = read_setting("OPENAI_MODEL", "gpt-5.4-mini")
    st.text(f"向量模型：{embed_model}\n回答模型：{answer_model}")
    st.caption("請使用合法且不含敏感資料的文件。關閉分頁或伺服器重啟後，需重新建立文件向量。")
    if st.button("清除本次工作", key="clear"):
        for name in ("document", "index", "query_cache", "evidence", "record"):
            st.session_state[name] = None
        # 累積嘗試次數保留，避免清除畫面後誤以為本次連線沒有使用API。

mode = "真實API" if real_api else "離線"
vector_model = embed_model if real_api else "人工關鍵字計數（4維）"

# ---------- 5. 第9週：輸入設定變更立即清除舊成果，只有按鈕才解析文件 ----------
st.header("① 上傳或選擇文件")
source = st.radio("資料來源", ["內建範例", "上傳檔案"], horizontal=True, key="source")
sample_name = st.selectbox("內建範例", ["sample.txt", "sample.csv", "sample.pdf", "sample.docx"], key="sample")
uploaded = st.file_uploader("上傳文件（選擇上傳檔案時使用，限1MB）",
                            type=["txt", "md", "csv", "pdf", "docx"], max_upload_size=1, key="upload")
encoding = st.selectbox("TXT／MD／CSV文字編碼", ["utf-8-sig", "cp950"], key="encoding")
# 預設和第10、11週App一樣用空白行分段，內建範例的結果才能和前兩週對照；長文件沒有空白行時改固定字元。
split = st.radio("切塊方式", ["空白行分段（第10、11週）", "固定字元（第9週）"], horizontal=True, key="split")
by_paragraph = split.startswith("空白行")
left, right = st.columns(2)
with left:
    chunk_size = st.slider("每段最多字元（chunk_size，固定字元時使用）", 40, 1000, 120, 20, key="chunk_size")
with right:
    overlap = st.number_input("相鄰片段重複字元（overlap，固定字元時使用）", min_value=0, max_value=999,
                              value=20, step=10, key="overlap")
st.caption("限單一文件、1MB、清理後20000字元與100段；空白行分段時每段最多1000字元。PDF需有文字層；掃描PDF不含OCR。")

filename, data = None, None
if source == "內建範例":
    filename, data = sample_name, (PACKAGE / "sample_data" / sample_name).read_bytes()
elif uploaded is not None:
    filename, data = uploaded.name, uploaded.getvalue()
actual_encoding = "utf-8-sig" if source == "內建範例" else encoding
input_id = (source, filename, sha256(data).hexdigest() if data is not None else None,
            actual_encoding, by_paragraph, chunk_size, int(overlap))
if st.session_state.get("input_id") != input_id:
    for name in ("document", "index", "query_cache", "evidence", "record"):
        st.session_state[name] = None
    st.session_state.input_id = input_id
index_settings = (mode, vector_model)
if st.session_state.get("index_settings") != index_settings:
    for name in ("index", "query_cache", "evidence", "record"):
        st.session_state[name] = None
    st.session_state.index_settings = index_settings

if st.button("處理文件", type="primary", key="prepare"):
    for name in ("document", "index", "query_cache", "evidence", "record"):
        st.session_state[name] = None
    try:
        if data is None:
            raise ValueError("請先上傳文件，或選擇內建範例。")
        with st.status("讀取 → 清理 → 切塊", expanded=True) as status:
            st.session_state.document = prepare_document(
                filename, data, actual_encoding, chunk_size, int(overlap), by_paragraph)
            status.update(label="文件處理完成（0次API）", state="complete", expanded=False)
    except Exception as exc:
        show_failure(exc)

document = st.session_state.document
if document is not None:
    st.text(f"目前文件：{document['filename']}｜{document['byte_size']} bytes")
    st.header("② 抽取與清理結果")
    a, b = st.columns(2)
    with a:
        st.metric("抽取後字元數", len(document["raw_text"]))
        with st.expander("查看抽取原文"):
            st.text(document["raw_text"])
    with b:
        st.metric("清理後字元數", len(document["cleaned_text"]))
        with st.expander("查看清理後文字"):
            st.text(document["cleaned_text"])
    st.header("③ 片段與來源位置")
    st.write(f"{document['split']}，共{len(document['chunks'])}段；位置對應清理後文字，end不包含。")
    st.dataframe(document["chunks"], hide_index=True, width="stretch")
    for item in document["chunks"]:
        with st.expander(f"片段{item['chunk_id']}｜位置{item['start']}～{item['end']}"):
            st.text(item["text"])
    st.download_button("下載清理後文字", document["cleaned_text"], "cleaned_text.txt", key="download_text")
    st.download_button("下載文件處理紀錄", json.dumps(document, ensure_ascii=False, indent=2),
                       "document_record.json", mime="application/json", key="download_document")

    # ---------- 6. 第10週：文件只向量化一次；手動重建才會再送一次 ----------
    st.header("④ 建立文件向量")
    st.caption("同一份文件可反覆提問。更換模式、文件或切塊設定後，必須重建向量。")
    if st.button("建立文件向量", key="embed_document"):
        for name in ("index", "query_cache", "evidence", "record"):
            st.session_state[name] = None
        try:
            with st.spinner("建立文件向量中…"):
                if real_api:
                    with open_client() as client:
                        st.session_state.api_attempts["文件向量"] += 1
                        vectors = embed_texts_checked(client, embed_model, [c["text"] for c in document["chunks"]])
                else:
                    vectors = [demo_vector(c["text"]) for c in document["chunks"]]
                st.session_state.index = {"mode": mode, "model": vector_model, "vectors": vectors}
        except Exception as exc:
            show_failure(exc)
    index = st.session_state.index
    if index is not None:
        st.success(f"文件向量已準備：{len(index['vectors'])}筆，每筆{len(index['vectors'][0])}維。")
        st.text(f"來源模式：{index['mode']}｜模型：{index['model']}")
        # 真實向量每筆上千維，全部列出會拖慢頁面；只列前5個數字，看出「每段一串數字」即可。
        with st.expander("查看文件向量（每筆只列前5個數字；數字本身不是原文，也不是答案）"):
            st.dataframe([{"chunk_id": c["chunk_id"], "前5個數字": str([round(x, 4) for x in v[:5]])}
                          for c, v in zip(document["chunks"], index["vectors"])], hide_index=True, width="stretch")

        # 問題與參數在表單外：任何變更先隱藏舊答案；按檢索按鈕才送新問題。
        st.header("⑤ 提問與檢索")
        question = st.text_input("你的問題", "活動地點在哪裡？", max_chars=300, key="question").strip()
        top_k = st.slider("最多取回幾段（top_k）", 1, min(10, len(document["chunks"])),
                          min(2, len(document["chunks"])), key="top_k") if len(document["chunks"]) > 1 else 1
        if len(document["chunks"]) == 1:
            st.caption("目前只有1段，top_k固定為1。")
        min_score = st.slider("檢索門檻（不是正確機率）", 0.0, 1.0, 0.2, 0.05, key="min_score")
        max_chars = st.slider("送給模型的資料上限（字元，含來源標籤）", 200, 6000, 4000, 200, key="max_chars")
        search_settings = (question, top_k, min_score, max_chars, answer_model)
        if st.session_state.get("search_settings") != search_settings:
            st.session_state.evidence = None
            st.session_state.record = None
            st.session_state.search_settings = search_settings
        if st.session_state.query_cache is not None and st.session_state.query_cache["question"] != question:
            st.session_state.query_cache = None

        if st.button("找證據／依目前參數重新排名", key="retrieve"):
            st.session_state.evidence = None
            st.session_state.record = None
            try:
                if not question:
                    raise ValueError("請先輸入問題。")
                cached = st.session_state.query_cache
                if cached is None:
                    if real_api:
                        with open_client() as client:
                            st.session_state.api_attempts["問題向量"] += 1
                            query_vector = embed_texts_checked(client, embed_model, [question])[0]
                    else:
                        query_vector = demo_vector(question)
                    cached = {"question": question, "vector": query_vector}
                    st.session_state.query_cache = cached
                st.session_state.evidence = retrieve_evidence(
                    document, index, question, cached["vector"], top_k, min_score, max_chars)
            except Exception as exc:
                show_failure(exc)

        evidence = st.session_state.evidence
        if evidence is not None:
            st.text(f"目前檢索問題：{evidence['question']}")
            with st.expander("查看問題向量（只列前5個數字）"):
                st.json({"維度": len(evidence["query_vector"]),
                         "前5個數字": [round(x, 4) for x in evidence["query_vector"][:5]]})
            selected = {h["chunk_id"] for h in evidence["hits"]}
            used = {h["chunk_id"] for h in evidence["sources"]}
            rows = [{"排名": i, "片段": h["chunk_id"], "相似度": h["score"],
                     "通過門檻": h["score"] >= min_score, "入選top_k": h["chunk_id"] in selected,
                     "放入context": h["chunk_id"] in used, "原文": h["text"]}
                    for i, h in enumerate(evidence["ranking"], 1)]
            if rows:
                st.dataframe(rows, hide_index=True, width="stretch")
            else:
                st.info("問題是零向量，沒有可比較的排名；離線規則不理解這個問題。")
            if not evidence["sources"]:
                st.warning("沒有可送出的證據：可能未通過門檻，或第一段超過context上限。回答時不呼叫模型。")

            # ---------- 7. 第11週：先預覽真正會送出的資料，再獨立觸發生成 ----------
            st.header("⑥ 送出前預覽：規則、問題與context")
            st.caption(f"檢索入選{len(evidence['hits'])}段；context實際容納{len(evidence['sources'])}段、{len(evidence['context'])}字元。")
            for item in evidence["sources"]:
                with st.expander(f"{item['label']}｜片段{item['chunk_id']}｜位置{item['start']}～{item['end']}"):
                    st.text(item["source"])
                    st.text(item["text"])
                    st.caption("回查清理後文字切片是否等於這段原文：")
                    st.write(document["cleaned_text"][item["start"]:item["end"]] == item["text"])
            with st.expander("查看完整回答規則與實際input", expanded=True):
                st.text(INSTRUCTIONS)
                st.text(evidence["input"] or "沒有證據，不會送出模型請求。")

            st.header("⑦ 依證據回答與核對")
            if not real_api:
                st.info("離線流程到此完成；下方紀錄不含模型答案。任意文件的語意搜尋與生成需切換真實模式並重建向量。")
                preview = {k: v for k, v in evidence.items() if k != "query_vector"}
                preview.update(document=document, answer=None, check="離線預覽：沒有呼叫模型", instructions=INSTRUCTIONS)
                st.download_button("下載離線檢索紀錄", json.dumps(preview, ensure_ascii=False, indent=2),
                                   "rag_record.json", mime="application/json", key="download_preview")
            elif st.button("依證據回答", type="primary", key="answer"):
                st.session_state.record = None
                try:
                    if not evidence["sources"]:
                        answer = INSUFFICIENT
                    else:
                        with open_client() as client:
                            st.session_state.api_attempts["回答"] += 1
                            with st.spinner("依本次證據回答中…"):
                                answer = generate_answer(client, answer_model, evidence)
                    st.session_state.record = make_record(
                        document, index, evidence, answer, answer_model, st.session_state.api_attempts)
                except Exception as exc:
                    show_failure(exc)

            record = st.session_state.record
            if record is not None:
                st.write(record["answer"])
                st.write("引用格式檢查：", record["check"])
                st.caption("相似度不是正確機率；引用格式通過不代表答案正確。請逐項回到上面的來源原文確認。")
                st.header("⑧ 下載問答紀錄")
                st.download_button("下載問答紀錄", json.dumps(record, ensure_ascii=False, indent=2),
                                   "rag_record.json", mime="application/json", key="download_answer")

st.caption("本次連線累積的API送出嘗試（含失敗；不是費用或token數）：")
st.json(st.session_state.api_attempts)
