"""
하이브리드 추천 엔진
- 앱 시작 시 1회만 로딩되어 메모리에 상주 (요청마다 재로딩 방지)
"""
import json
import time
import logging
from pathlib import Path
from typing import List, Tuple
from typing import List, Tuple, Optional, Set
from .genre_filter import resolve_allowed_categories, apply_category_filter
from .query_encoder import TitleMatcher, build_query_vector

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
        self.title_matcher = None

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
        # 제목 매칭용 임베딩 복원 (FAISS 인덱스에서 역추출)
        try:
            stored = self.faiss_index.reconstruct_n(0, self.faiss_index.ntotal)
            self.title_matcher = TitleMatcher(self.books, np.asarray(stored, dtype=np.float32))
            logger.info(f"TitleMatcher ready ({len(self.title_matcher._lookup)} titles)")
        except Exception as e:
            logger.warning(f"TitleMatcher init failed, falling back to text encoding: {e}")
            self.title_matcher = None

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
        self, query_vec: np.ndarray, top_k: int, alpha: float,
        allowed_categories: Optional[Set[str]] = None,
    ) -> Tuple[pd.DataFrame, dict]:
        """FAISS 검색 → 하이브리드 스코어 → 카테고리 필터"""
        # 필터가 있으면 여유 있게 가져온다 (over-fetch)
        multiplier = 10 if allowed_categories else 3
        search_k = min(top_k * multiplier, self.faiss_index.ntotal)
        similarities, indices = self.faiss_index.search(query_vec, search_k)

        results = self.books.iloc[indices[0]].copy()
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

        final, applied, relaxed = apply_category_filter(
            results, allowed_categories, top_k
        )

        meta = {
            "filter_applied": applied,
            "filter_relaxed": relaxed,
            "allowed_categories": sorted(allowed_categories) if allowed_categories else [],
        }
        return final.reset_index(drop=True), meta

    def recommend_path_a(
        self, books: List[str], top_k: int = 10, alpha: float = 0.7
    ) -> Tuple[pd.DataFrame, float, dict]:
        """Path A: 좋아하는 책 기반 추천"""
        start = time.perf_counter()

        query_vec, match_meta = build_query_vector(
            books, self.title_matcher, self.sbert_model
        )
        results, meta = self._search_and_blend(query_vec, top_k, alpha)

        # 입력한 책 자신은 결과에서 제외
        if match_meta["matched_titles"]:
            results = results[~results["title"].isin(match_meta["matched_titles"])]
            results = results.head(top_k).reset_index(drop=True)

        meta.update(match_meta)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return results, elapsed_ms, meta

    def recommend_path_b(
        self, tags: List[str], top_k: int = 10, alpha: float = 0.7
    ) -> Tuple[pd.DataFrame, float, dict]:
        """Path B: 태그 기반 추천 (장르 태그는 카테고리 필터로도 작동)"""
        start = time.perf_counter()

        tag_texts = [self.tag_templates.get(t, t) for t in tags]
        combined = " . ".join(tag_texts)
        query_vec = self._encode_query([combined])

        allowed = resolve_allowed_categories(tags)
        results, meta = self._search_and_blend(query_vec, top_k, alpha, allowed)

        elapsed_ms = (time.perf_counter() - start) * 1000
        return results, elapsed_ms, meta