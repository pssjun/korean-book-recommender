"""
하이브리드 추천 엔진
- 앱 시작 시 1회만 로딩되어 메모리에 상주 (요청마다 재로딩 방지)
"""
import json
import time
import logging
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class HybridRecommender:
    def __init__(self, data_dir: str = "data", model_dir: str = "models"):
        self.data_dir = Path(data_dir)
        self.model_dir = Path(model_dir)

        self.config = None
        self.books = None
        self.tag_templates = None
        self.faiss_index = None
        self.sbert_model = None
        self._loaded = False

    def load(self):
        """앱 시작 시 1회 호출 - 모든 자원을 메모리에 로딩"""
        start = time.time()
        logger.info("Loading recommender resources...")

        with open(self.data_dir / "config.json", "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.books = pd.read_parquet(self.data_dir / "books_streamlit.parquet")

        with open(self.data_dir / "tag_templates.json", "r", encoding="utf-8") as f:
            self.tag_templates = json.load(f)

        self.faiss_index = faiss.read_index(str(self.model_dir / "faiss_index.bin"))

        self.sbert_model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            device="cpu"
        )
        # ---- 데이터/인덱스 정합성 검증 (fail fast) ----
        if self.faiss_index.ntotal != len(self.books):
            raise RuntimeError(
                f"Data/Index mismatch: index={self.faiss_index.ntotal}, "
                f"books={len(self.books)}. "
                f"Run `python scripts/build_index.py` to rebuild the index."
            )
        self._loaded = True
        elapsed = time.time() - start
        logger.info(
            f"Recommender loaded in {elapsed:.2f}s "
            f"(books={len(self.books)}, index={self.faiss_index.ntotal})"
        )

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def _encode_query(self, texts: List[str]) -> np.ndarray:
        """텍스트 리스트를 하나의 취향 벡터로 변환"""
        embeds = self.sbert_model.encode(
            texts, convert_to_numpy=True, normalize_embeddings=True
        )
        vec = embeds.mean(axis=0, keepdims=True).astype(np.float32)
        vec /= np.linalg.norm(vec)
        return vec

    def _search_and_blend(
        self, query_vec: np.ndarray, top_k: int, alpha: float
    ) -> pd.DataFrame:
        """FAISS 검색 후 인기 신호와 하이브리드 결합"""
        search_k = min(top_k * 3, self.faiss_index.ntotal)
        similarities, indices = self.faiss_index.search(query_vec, search_k)

        results = self.books.iloc[indices[0]].copy()
        results["content_similarity"] = similarities[0]

        # 유사도 정규화 (0~1)
        sim_min = results["content_similarity"].min()
        sim_max = results["content_similarity"].max()
        if sim_max > sim_min:
            results["content_normalized"] = (
                (results["content_similarity"] - sim_min) / (sim_max - sim_min)
            )
        else:
            results["content_normalized"] = 1.0

        # 하이브리드 점수
        results["hybrid_score"] = (
            alpha * results["content_normalized"]
            + (1 - alpha) * results["popularity_score"]
        )

        results = results.sort_values("hybrid_score", ascending=False).head(top_k)
        return results.reset_index(drop=True)

    def recommend_path_a(
        self, books: List[str], top_k: int = 10, alpha: float = 0.7
    ) -> Tuple[pd.DataFrame, float]:
        """Path A: 좋아하는 책 기반 추천"""
        start = time.perf_counter()
        query_vec = self._encode_query(books)
        results = self._search_and_blend(query_vec, top_k, alpha)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return results, elapsed_ms

    def recommend_path_b(
        self, tags: List[str], top_k: int = 10, alpha: float = 0.7
    ) -> Tuple[pd.DataFrame, float]:
        """Path B: 태그 기반 추천"""
        start = time.perf_counter()
        tag_texts = [self.tag_templates.get(t, t) for t in tags]
        combined = " . ".join(tag_texts)
        query_vec = self._encode_query([combined])
        results = self._search_and_blend(query_vec, top_k, alpha)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return results, elapsed_ms