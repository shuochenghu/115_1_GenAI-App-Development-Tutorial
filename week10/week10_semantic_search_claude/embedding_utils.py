"""第 10 週｜Embedding、相似度與語意搜尋工具（Claude 版）。

本模組把第 9 週產出的 chunks 轉成向量，並提供最小語意搜尋與 ChromaDB 索引。
函式命名對齊 Codex 版 `embedding_utils.py`，方便兩版對照：

    get_embedding / cosine_similarity / search_chunks
    build_chroma_collection / query_chroma

Claude 版額外提供 `local_demo_embed()`「離線假 embedding」：
不連網、不花錢，只為讓沒有 API key 的學生也能把整條搜尋管線跑完、驗證邏輯。
它沒有真正語意，語意搜尋效果一定要用真 Embeddings API 才算數。
"""

from __future__ import annotations

import hashlib
import os

import numpy as np
from dotenv import load_dotenv


DEFAULT_EMBED_MODEL = "text-embedding-3-small"  # 1536 維；可用 OPENAI_EMBED_MODEL 覆蓋
OFFLINE_DIM = 256  # 離線假 embedding 維度


def get_secret(name: str, default: str | None = None) -> str | None:
    """先讀 Streamlit Secrets（若在 Streamlit 環境），再讀本機 .env / 環境變數。"""
    try:
        import streamlit as st  # 延遲載入：純 Notebook 執行時不需要 streamlit
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    load_dotenv()
    return os.getenv(name, default)


# --------------------------------------------------------------------------- #
# 1. 產生向量：真 Embeddings API 與離線假 embedding
# --------------------------------------------------------------------------- #
def local_demo_embed(text: str, dim: int = OFFLINE_DIM) -> list[float]:
    """離線假 embedding：用雜湊把文字攤成固定長度向量。

    以「字元 + 相鄰字元 bigram + 空白斷詞」當特徵，讓中文即使沒有空格，
    只要有共同字詞就會產生重疊（向量相近）。相同文字→相同向量，
    但這只是**字面重疊**、**沒有真正語意**（貓與小貓不會比貓與股票更近）。
    僅供沒有 API key 時驗證 cosine / 搜尋 / ChromaDB 的程式邏輯。
    """
    vector = [0.0] * dim
    lowered = text.lower()
    chars = [c for c in lowered if not c.isspace()]
    grams = list(chars)
    grams += [chars[i] + chars[i + 1] for i in range(len(chars) - 1)]
    grams += lowered.split()
    if not grams:
        grams = [lowered]
    for gram in grams:
        bucket = int(hashlib.md5(gram.encode("utf-8")).hexdigest(), 16) % dim
        vector[bucket] += 1.0
    return vector


def get_embedding(
    text: str,
    offline: bool = False,
    model: str | None = None,
    dimensions: int | None = None,
) -> list[float]:
    """把單一段文字轉成向量。offline=True 時使用離線假 embedding。"""
    if not text or not text.strip():
        raise ValueError("輸入文字為空，無法產生 embedding。")
    if offline:
        return local_demo_embed(text)
    return embed_texts([text], model=model, dimensions=dimensions)[0]


def embed_texts(
    texts: list[str],
    offline: bool = False,
    model: str | None = None,
    dimensions: int | None = None,
) -> list[list[float]]:
    """批次把多段文字轉成向量（建索引時用批次比逐筆省成本與延遲）。"""
    cleaned = [t for t in texts if t and t.strip()]
    if not cleaned:
        raise ValueError("沒有可產生 embedding 的非空文字。")

    if offline:
        return [local_demo_embed(t) for t in cleaned]

    from openai import OpenAI

    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("找不到 OPENAI_API_KEY，請先設定 `.env` 或 Streamlit Secrets。")

    client = OpenAI(api_key=api_key)
    selected_model = model or get_secret("OPENAI_EMBED_MODEL", DEFAULT_EMBED_MODEL)
    kwargs = {"model": selected_model, "input": cleaned}
    if dimensions:
        kwargs["dimensions"] = dimensions
    try:
        response = client.embeddings.create(**kwargs)
    except Exception as exc:  # noqa: BLE001 - 轉成清楚訊息往上丟
        raise RuntimeError(f"呼叫 Embeddings API 失敗：{exc}") from exc
    return [item.embedding for item in response.data]


# --------------------------------------------------------------------------- #
# 2. 相似度與最小語意搜尋（不需向量資料庫）
# --------------------------------------------------------------------------- #
def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """計算兩個向量的 cosine 相似度，範圍約 -1 ~ 1；任一為零向量時回 0。"""
    a = np.asarray(vec_a, dtype=float)
    b = np.asarray(vec_b, dtype=float)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def search_chunks(
    query: str,
    chunks: list[dict],
    top_k: int = 5,
    offline: bool = False,
) -> list[dict]:
    """最小語意搜尋：把 query 轉成向量，與每個 chunk 的向量算 cosine，回傳 top-k。

    chunks 每個元素需含 `text` 與 `embedding`（可用 embed_texts 事先算好）。
    回傳的每筆含原 chunk 欄位（不含 embedding）加上 `score`（cosine 相似度）。
    """
    if not query or not query.strip():
        raise ValueError("查詢字串為空。")
    if not chunks:
        return []

    query_vector = get_embedding(query, offline=offline)
    scored = []
    for chunk in chunks:
        embedding = chunk.get("embedding")
        if embedding is None:
            continue
        score = cosine_similarity(query_vector, embedding)
        payload = {key: value for key, value in chunk.items() if key != "embedding"}
        payload["score"] = round(score, 4)
        scored.append(payload)

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]


# --------------------------------------------------------------------------- #
# 3. ChromaDB：向量資料庫主線
# --------------------------------------------------------------------------- #
def build_chroma_collection(
    chunks: list[dict],
    offline: bool = False,
    name: str = "week10_docs",
    embeddings: list[list[float]] | None = None,
):
    """把 chunks 建成 ChromaDB collection（in-memory）。

    每個 chunk 需含 `chunk_id` 與 `text`；start/end/source 等會存進 metadata，
    讓第 11 週能顯示「答案來自哪個片段」。使用 cosine 距離空間。
    """
    if not chunks:
        raise ValueError("沒有可建立索引的 chunks。")

    import chromadb

    texts = [chunk["text"] for chunk in chunks]
    if embeddings is None:
        embeddings = embed_texts(texts, offline=offline)

    client = chromadb.EphemeralClient()
    try:
        client.delete_collection(name)
    except Exception:
        pass
    collection = client.create_collection(name, metadata={"hnsw:space": "cosine"})
    collection.add(
        ids=[str(chunk["chunk_id"]) for chunk in chunks],
        documents=texts,
        embeddings=[list(vector) for vector in embeddings],
        metadatas=[
            {
                "chunk_id": int(chunk.get("chunk_id", index)),
                "start": int(chunk.get("start", 0)),
                "end": int(chunk.get("end", 0)),
                "source": str(chunk.get("source", "")),
            }
            for index, chunk in enumerate(chunks)
        ],
    )
    return collection


def query_chroma(
    collection,
    query: str,
    top_k: int = 5,
    offline: bool = False,
) -> list[dict]:
    """對 ChromaDB collection 做 top-k 查詢，回傳含來源與相似度的結果。"""
    if not query or not query.strip():
        raise ValueError("查詢字串為空。")

    query_vector = get_embedding(query, offline=offline)
    result = collection.query(query_embeddings=[list(query_vector)], n_results=top_k)

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    hits = []
    for document, metadata, distance in zip(documents, metadatas, distances):
        hits.append({
            "text": document,
            "metadata": metadata,
            "distance": round(float(distance), 4),
            "score": round(1.0 - float(distance), 4),  # cosine 距離 → 相似度
        })
    return hits
