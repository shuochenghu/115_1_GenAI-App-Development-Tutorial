"""第 11 週 Embeddings 與 ChromaDB 檢索 helper。

本模組把「文字轉向量」和「向量資料庫」放在同一層。離線模式使用可重現的假
embedding，供無 API key 的流程測試；真語意模式才呼叫 OpenAI Embeddings API。
兩種模式都寫入 ChromaDB，因此學生能用同一套 UI 觀察資料庫查詢流程。
"""

from __future__ import annotations

import hashlib
import os

from dotenv import load_dotenv
import numpy as np


DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
OFFLINE_DIMENSIONS = 256


def get_secret(name: str, default: str | None = None) -> str | None:
    """依序讀取 Streamlit Secrets、`.env` 與作業系統環境變數。"""
    try:
        import streamlit as st

        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        # Notebook、單元測試或 secrets 尚未建立時，仍要允許本機離線流程執行。
        pass
    load_dotenv()
    return os.getenv(name, default)


def local_demo_embed(text: str, dimensions: int = OFFLINE_DIMENSIONS) -> list[float]:
    """用字元、雙字元與詞彙雜湊產生固定長度的本機假 embedding。

    相同文字會得到相同向量，適合驗證 ChromaDB 寫入與查詢；它不具備真正語意，
    因此離線模式的搜尋品質不能代表 OpenAI Embeddings API。
    """
    vector = np.zeros(dimensions, dtype=float)
    normalized = text.lower().strip()
    characters = [character for character in normalized if not character.isspace()]
    features = list(characters)
    features += [characters[index] + characters[index + 1] for index in range(len(characters) - 1)]
    features += normalized.split()

    if not features:
        return vector.tolist()

    for feature in features:
        digest = hashlib.md5(feature.encode("utf-8")).hexdigest()
        bucket = int(digest, 16) % dimensions
        vector[bucket] += 1.0

    norm = np.linalg.norm(vector)
    return (vector / norm).tolist() if norm else vector.tolist()


def embed_texts(
    texts: list[str],
    *,
    offline: bool = True,
    model: str | None = None,
) -> list[list[float]]:
    """批次將非空文字轉成 embedding，並維持輸入與輸出的順序一致。"""
    if not texts or any(not text.strip() for text in texts):
        raise ValueError("texts 必須是非空文字清單。")

    if offline:
        return [local_demo_embed(text) for text in texts]

    from openai import OpenAI

    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("找不到 OPENAI_API_KEY，請先設定 `.env` 或 Streamlit Secrets。")

    selected_model = model or get_secret("OPENAI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
    client = OpenAI(api_key=api_key)
    try:
        response = client.embeddings.create(model=selected_model, input=texts)
    except Exception as exc:
        raise RuntimeError(f"呼叫 Embeddings API 失敗：{exc}") from exc
    return [item.embedding for item in response.data]


def build_chroma_index(
    chunks: list[dict],
    *,
    offline: bool = True,
    model: str | None = None,
):
    """建立 in-memory ChromaDB collection，保存文字、向量與來源 metadata。

    每次重新索引都建立新的 `EphemeralClient()`，避免舊檔案的 chunk 殘留。回傳 client
    是為了讓 Streamlit session 保留其生命週期；關閉 App 後資料不會持久化到磁碟。
    """
    if not chunks:
        raise ValueError("沒有 chunks，無法建立 ChromaDB 索引。")

    try:
        import chromadb
    except ImportError as exc:
        raise RuntimeError("尚未安裝 chromadb，請先執行 `pip install -r requirements.txt`。") from exc

    texts = [str(chunk.get("text", "")) for chunk in chunks]
    vectors = embed_texts(texts, offline=offline, model=model)
    client = chromadb.EphemeralClient()
    # cosine 設定的是 collection 的距離函式；下方 metadatas 保存各 chunk 的來源。
    collection = client.create_collection(
        name="week11_documents",
        configuration={"hnsw": {"space": "cosine"}},
    )
    collection.add(
        ids=[str(chunk.get("chunk_id", index)) for index, chunk in enumerate(chunks)],
        documents=texts,
        embeddings=vectors,
        metadatas=[
            {
                "chunk_id": int(chunk.get("chunk_id", index)),
                "source": str(chunk.get("source", "未知")),
                "start": int(chunk.get("start", 0)),
                "end": int(chunk.get("end", 0)),
            }
            for index, chunk in enumerate(chunks)
        ],
    )
    return client, collection


def query_chroma_index(
    collection,
    query: str,
    *,
    top_k: int = 4,
    min_score: float = 0.20,
    offline: bool = True,
    model: str | None = None,
) -> list[dict]:
    """查詢 ChromaDB，將巢狀結果攤平成可直接組成 context 的 hits。

    ChromaDB 的 cosine distance 越小越接近。教材用 `1 - distance` 顯示為 score，
    方便延續第 10 週閱讀方式；score 只是排序指標，不是正確機率。
    """
    if not query.strip():
        raise ValueError("問題不可為空。")
    if top_k <= 0:
        raise ValueError("top_k 必須大於 0。")
    if not -1.0 <= min_score <= 1.0:
        raise ValueError("min_score 必須介於 -1 與 1 之間。")

    item_count = int(collection.count())
    if item_count == 0:
        return []

    query_vector = embed_texts([query], offline=offline, model=model)[0]
    raw_result = collection.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, item_count),
        include=["documents", "metadatas", "distances"],
    )

    ids = raw_result.get("ids", [[]])[0]
    documents = raw_result.get("documents", [[]])[0]
    metadatas = raw_result.get("metadatas", [[]])[0]
    distances = raw_result.get("distances", [[]])[0]

    hits = []
    for rank, (item_id, document, metadata, distance) in enumerate(
        zip(ids, documents, metadatas, distances),
        start=1,
    ):
        score = 1.0 - float(distance)
        if score < min_score:
            continue
        item = dict(metadata or {})
        item.update({
            "id": item_id,
            "rank": rank,
            "text": document or "",
            "distance": round(float(distance), 4),
            "score": round(score, 4),
        })
        hits.append(item)
    return hits
