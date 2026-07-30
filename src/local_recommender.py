"""
로컬 추론 폴백 모듈

추천 API를 사용할 수 없을 때 Streamlit 프로세스 내에서 직접 추론한다.
API 서버와 동일한 로직·동일한 데이터를 사용하므로 결과가 일치한다.
"""
import json
import time
from pathlib import Path
from typing import List, Tuple
import sys
sys.path.append(".")
from api.genre_filter import resolve_allowed_categories, apply_category_filter

import numpy as np
import pandas as pd
import faiss
import streamlit as st
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


@st.cache_resource(show_spinner=False)
def _load_resources():
    """모델·인덱스·데이터 로딩 (세션 간 캐싱)"""
    data_dir = Path("data")
    model_dir = Path("models")

    books = pd.read_parquet(data_dir / "books_streamlit.parquet")

    with open(data_dir / "tag_templates.json", "r", encoding="utf-8") as f:
        tag_templates = json.load(f)

    index = faiss.read_index(str(model_dir / "faiss_index.bin"))

    # API 서버와 동일한 정합성 검증
    if index.ntotal != len(books):
        raise RuntimeError(
            f"Data/Index mismatch: index={index.ntotal}, books={len(books)}"
        )

    model = SentenceTransformer(MODEL_NAME, device="cpu")

    return books, tag_templates, index, model


def _encode_query(model, texts: List[str]) -> np.ndarray:
    embeds = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    vec = embeds.mean(axis=0, keepdims=True).astype(np.float32)
    vec /= np.linalg.norm(vec)
    return vec


def _search_and_blend(books, index, query_vec, top_k: int, alpha: float,
                      allowed_categories=None):
    multiplier = 10 if allowed_categories else 3
    search_k = min(top_k * multiplier, index.ntotal)
    similarities, indices = index.search(query_vec, search_k)

    results = books.iloc[indices[0]].copy()
    results["content_similarity"] = similarities[0]

    sim_min = results["content_similarity"].min()
    sim_max = results["content_similarity"].max()
    if sim_max > sim_min:
        results["content_normalized"] = (
            (results["content_similarity"] - sim_min) / (sim_max - sim_min)
        )
    else:
        results["content_normalized"] = 1.0

    results["hybrid_score"] = (
        alpha * results["content_normalized"]
        + (1 - alpha) * results["popularity_score"]
    )
    results = results.sort_values("hybrid_score", ascending=False)

    final, applied, relaxed = apply_category_filter(results, allowed_categories, top_k)
    meta = {
        "filter_applied": applied,
        "filter_relaxed": relaxed,
        "allowed_categories": sorted(allowed_categories) if allowed_categories else [],
    }
    return final.reset_index(drop=True), meta

def _to_api_format(results, path, alpha, query_summary, index_total, elapsed_ms, meta):
    items = []
    for i, row in results.iterrows():
        items.append({
            "rank": i + 1,
            "title": str(row["title"]),
            "author": str(row.get("author_clean", "")),
            "category_main": str(row.get("cat_main", "")),
            "category_mid": str(row.get("cat_mid", "")),
            "content_similarity": float(row["content_similarity"]),
            "popularity_score": float(row["popularity_score"]),
            "hybrid_score": float(row["hybrid_score"]),
            "cover_url": str(row["cover_url"]) if row.get("cover_url") else None,
            "link": str(row["link"]) if row.get("link") else None,
            "description": str(row["description"]) if row.get("description") else None,
        })

    return {
        "path": path,
        "alpha": alpha,
        "query_summary": query_summary,
        "total_books_searched": index_total,
        "elapsed_ms": round(elapsed_ms, 2),
        "filter_applied": meta["filter_applied"],
        "filter_relaxed": meta["filter_relaxed"],
        "allowed_categories": meta["allowed_categories"],
        "results": items,
    }


def recommend_path_a(books_query, top_k: int = 10, alpha: float = 0.7) -> dict:
    books, _, index, model = _load_resources()
    start = time.perf_counter()
    query_vec = _encode_query(model, books_query)
    results, meta = _search_and_blend(books, index, query_vec, top_k, alpha)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return _to_api_format(
        results, "A", alpha, ", ".join(books_query), index.ntotal, elapsed_ms, meta
    )


def recommend_path_b(tags, top_k: int = 10, alpha: float = 0.7) -> dict:
    books, tag_templates, index, model = _load_resources()
    start = time.perf_counter()

    tag_texts = [tag_templates.get(t, t) for t in tags]
    combined = " . ".join(tag_texts)
    query_vec = _encode_query(model, [combined])

    allowed = resolve_allowed_categories(tags)
    results, meta = _search_and_blend(books, index, query_vec, top_k, alpha, allowed)

    elapsed_ms = (time.perf_counter() - start) * 1000
    return _to_api_format(
        results, "B", alpha, ", ".join(tags), index.ntotal, elapsed_ms, meta
    )

def get_stats() -> dict:
    """로컬 자원 상태 (헬스체크 대체)"""
    books, _, index, _ = _load_resources()
    return {
        "total_books": len(books),
        "index_size": index.ntotal,
    }