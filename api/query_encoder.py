"""
쿼리 임베딩 생성

문서 임베딩은 '제목 + 카테고리 + 저자 + 소개문' 형식으로 저장되어 있다.
사용자가 제목만 입력하면 형식이 달라 유사도 변별력이 떨어지므로
(쿼리-문서 비대칭), DB에 있는 책은 저장된 임베딩을 그대로 사용한다.

  입력이 DB에 있음  → 저장된 임베딩 사용 (형식 일치)
  입력이 DB에 없음  → 텍스트 인코딩 폴백
"""
import logging
import re
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def normalize_title(s: str) -> str:
    """제목 매칭용 정규화 — 부제·괄호·공백·기호 제거"""
    s = str(s).lower()
    s = re.sub(r"[-–—]\s.*$", "", s)          # 부제 제거
    s = re.sub(r"[\(\[].*?[\)\]]", "", s)     # 괄호 내용 제거
    s = re.sub(r"[^\w가-힣]", "", s)           # 기호·공백 제거
    return s.strip()


class TitleMatcher:
    """도서 제목으로 저장된 임베딩을 찾는다"""

    def __init__(self, books: pd.DataFrame, embeddings: np.ndarray):
        self.books = books
        self.embeddings = embeddings
        # 정규화 제목 → 행 인덱스 (인기순으로 대표 1건)
        norm = books["title"].map(normalize_title)
        order = books["popularity_score"].fillna(0).values.argsort()[::-1]
        self._lookup = {}
        for i in order:
            key = norm.iloc[i]
            if key and key not in self._lookup:
                self._lookup[key] = i

    def find(self, query: str) -> Optional[int]:
        """제목 매칭. 완전일치 → 부분포함 순으로 시도"""
        key = normalize_title(query)
        if not key:
            return None
        if key in self._lookup:
            return self._lookup[key]
        # 부분 포함 (입력이 저장 제목에 포함되거나 그 반대)
        for stored_key, idx in self._lookup.items():
            if len(key) >= 4 and (key in stored_key or stored_key in key):
                return idx
        return None


def build_query_vector(
    queries: List[str],
    matcher: Optional[TitleMatcher],
    model,
) -> Tuple[np.ndarray, dict]:
    """
    입력 목록에서 취향 벡터 생성

    Returns:
        (정규화된 384차원 벡터, 매칭 정보)
    """
    vectors = []
    matched, unmatched = [], []

    for q in queries:
        idx = matcher.find(q) if matcher else None
        if idx is not None:
            vectors.append(matcher.embeddings[idx])
            matched.append(str(matcher.books.iloc[idx]["title"]))
        else:
            vectors.append(
                model.encode([q], convert_to_numpy=True, normalize_embeddings=True)[0]
            )
            unmatched.append(q)

    vec = np.mean(vectors, axis=0).astype(np.float32)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm

    meta = {
        "matched_count": len(matched),
        "total_count": len(queries),
        "matched_titles": matched,
        "unmatched_queries": unmatched,
    }
    if unmatched:
        logger.info(f"Title match: {len(matched)}/{len(queries)}, unmatched={unmatched}")

    return vec.reshape(1, -1), meta