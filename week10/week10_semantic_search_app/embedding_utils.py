"""第 10 週 Embedding、相似度與語意搜尋 helper。

本模組的教學主線是「先理解向量搜尋資料流，再接真實 API」：
1. `local_demo_embed()` 用本機假 embedding 跑通流程，不需要 API key。
2. `embed_texts()` 在真語意模式才呼叫 OpenAI Embeddings API。
3. `build_embedding_index()` 與 `search_index()` 使用最小的 list[dict] 索引，
   讓學生先看懂資料結構，再理解 ChromaDB / FAISS 的必要性。
"""

from __future__ import annotations

import hashlib
import os

from dotenv import load_dotenv
import numpy as np


DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
OFFLINE_DIMENSIONS = 256


def get_secret(name: str, default: str | None = None) -> str | None:
    """讀取設定值，優先使用 Streamlit Secrets，再退回 `.env` 與環境變數。"""
    try:
        import streamlit as st

        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        # Notebook、單元測試或 secrets 尚未建立時，不應因讀取設定而中斷本機流程。
        pass
    load_dotenv()
    return os.getenv(name, default)


def local_demo_embed(text: str, dimensions: int = OFFLINE_DIMENSIONS) -> list[float]:
    """用雜湊產生固定長度假 embedding，供無 API key 的課堂流程測試使用。

    參數：
        text: 要轉成向量的文字。
        dimensions: 輸出向量長度；固定長度才能做 cosine similarity。

    回傳：
        固定長度的 float list。

    教學重點：
    - 相同文字會得到相同向量，方便測試索引與搜尋流程。
    - 它只反映字面重疊，不具備真正語意；正式搜尋效果需使用 Embeddings API。
    """
    vector = np.zeros(dimensions, dtype=float)
    normalized = text.lower().strip()
    chars = [char for char in normalized if not char.isspace()]
    features = list(chars)
    features += [chars[index] + chars[index + 1] for index in range(len(chars) - 1)]
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
    """批次把多段文字轉成 embedding。

    參數：
        texts: 要轉向量的文字清單。
        offline: True 時使用本機假 embedding；False 時才呼叫 OpenAI API。
        model: OpenAI embedding model 名稱，未指定時讀環境變數。

    回傳：
        與 `texts` 順序一致的向量清單。

    可能錯誤：
        ValueError: 沒有可處理的非空文字。
        RuntimeError: 真語意模式缺少 API key 或 API 呼叫失敗。
    """
    if not texts or any(not text.strip() for text in texts):
        raise ValueError("texts 必須是非空文字清單。")

    if offline:
        return [local_demo_embed(text) for text in texts]

    from openai import OpenAI

    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("找不到 OPENAI_API_KEY，請先設定 `.env` 或 Streamlit Secrets。")

    selected_model = model or get_secret(
        "OPENAI_EMBEDDING_MODEL",
        get_secret("OPENAI_EMBED_MODEL", DEFAULT_EMBEDDING_MODEL),
    )
    client = OpenAI(api_key=api_key)
    try:
        response = client.embeddings.create(model=selected_model, input=texts)
    except Exception as exc:
        raise RuntimeError(f"呼叫 Embeddings API 失敗：{exc}") from exc
    return [item.embedding for item in response.data]


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """計算兩個向量的 cosine similarity，任一零向量時回傳 0。"""
    a = np.asarray(vec_a, dtype=float)
    b = np.asarray(vec_b, dtype=float)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def build_embedding_index(
    chunks: list[dict],
    *,
    offline: bool = True,
    model: str | None = None,
) -> list[dict]:
    """把 chunks 加上 embedding，形成最小可搜尋索引。

    回傳值仍是 `list[dict]`，而不是直接引入資料庫。這讓學生先看懂每筆資料
    如何保存 `text`、`source`、`start`、`end` 與 `embedding`，再進入向量資料庫。
    """
    if not chunks:
        raise ValueError("沒有 chunks，無法建立索引。")

    texts = [chunk["text"] for chunk in chunks]
    vectors = embed_texts(texts, offline=offline, model=model)
    indexed = []
    for chunk, vector in zip(chunks, vectors):
        item = dict(chunk)
        item["embedding"] = vector
        indexed.append(item)
    return indexed


def search_index(
    query: str,
    indexed_chunks: list[dict],
    *,
    top_k: int = 5,
    offline: bool = True,
    model: str | None = None,
) -> list[dict]:
    """使用 query embedding 搜尋最相近的 chunks。

    回傳結果會移除原始 embedding，避免把大量向量直接丟到 Streamlit 前端顯示。
    """
    if not query.strip():
        raise ValueError("查詢內容不可為空。")
    if top_k <= 0:
        raise ValueError("top_k 必須大於 0。")

    query_vector = embed_texts([query], offline=offline, model=model)[0]
    results = []
    for chunk in indexed_chunks:
        score = cosine_similarity(query_vector, chunk["embedding"])
        payload = {key: value for key, value in chunk.items() if key != "embedding"}
        payload["score"] = round(score, 4)
        results.append(payload)

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


def build_chroma_collection(indexed_chunks: list[dict], name: str = "week10_docs"):
    """選讀：把已含 embedding 的 chunks 放入 ChromaDB in-memory collection。

    ChromaDB 適合第 11 週銜接來源引用，因為它能把向量、文字與 metadata 綁在一起。
    本函式不在正式 app 主流程使用；若環境未安裝 `chromadb`，會提供清楚錯誤。
    """
    try:
        import chromadb
    except ImportError as exc:
        raise RuntimeError("尚未安裝 chromadb；若要跑選讀示範，請先 `pip install chromadb`。") from exc

    client = chromadb.EphemeralClient()
    try:
        client.delete_collection(name)
    except Exception:
        pass

    collection = client.create_collection(name, metadata={"hnsw:space": "cosine"})
    collection.add(
        ids=[str(chunk["chunk_id"]) for chunk in indexed_chunks],
        documents=[chunk["text"] for chunk in indexed_chunks],
        embeddings=[chunk["embedding"] for chunk in indexed_chunks],
        metadatas=[
            {
                "chunk_id": int(chunk.get("chunk_id", index)),
                "source": str(chunk.get("source", "")),
                "start": int(chunk.get("start", 0)),
                "end": int(chunk.get("end", 0)),
            }
            for index, chunk in enumerate(indexed_chunks)
        ],
    )
    return collection
