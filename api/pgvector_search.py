"""
PGVector 기반 검색 백엔드

FAISS와 동일한 입출력을 제공하되, 장르 필터를 SQL WHERE 절로 처리한다.
FAISS는 벡터만 다루므로 over-fetch 후 후처리가 필요했지만,
여기서는 필터를 먼저 적용한 뒤 그 안에서 유사도 검색을 수행한다.
"""
import os
import time
import logging
from typing import List, Optional, Set, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# PGVector는 선택적 의존성 (로컬 비교 실험용)
try:
    import psycopg
    from pgvector.psycopg import register_vector
    _PG_AVAILABLE = True
except ImportError:
    _PG_AVAILABLE = False
    logger.debug("psycopg/pgvector not installed - PGVector backend unavailable")

DSN = os.getenv("PG_DSN", "postgresql://bookuser:bookpass@localhost:5432/bookdb")


class PgVectorSearcher:
    """PostgreSQL + pgvector 검색"""

    def __init__(self, dsn: str = DSN):
        self.dsn = dsn
        self._conn = None

    def connect(self):
        """연결 수립 (앱 기동 시 1회)"""
        if not _PG_AVAILABLE:
            raise RuntimeError(
                "psycopg/pgvector not installed. "
                "Run: pip install -r requirements-dev.txt"
            )
        self._conn = psycopg.connect(self.dsn, autocommit=True)
        register_vector(self._conn)
        logger.info("PgVector connected")

    @property
    def is_connected(self) -> bool:
        return self._conn is not None and not self._conn.closed

    def count(self) -> int:
        with self._conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM books")
            return cur.fetchone()[0]

    def search(
        self,
        query_vec: np.ndarray,
        top_k: int = 10,
        alpha: float = 0.7,
        allowed_categories: Optional[Set[str]] = None,
        exclude_ids: Optional[List[int]] = None,
    ) -> Tuple[pd.DataFrame, dict]:
        """
        하이브리드 검색

        FAISS 대비 차이:
          - 카테고리 필터를 WHERE 절로 먼저 적용 (over-fetch 불필요)
          - 메타데이터가 같은 행에 있어 별도 조회 없음
        """
        vec = query_vec.reshape(-1).astype(np.float32)

        # <#> 는 음의 내적. 정규화된 벡터이므로 -(<#>) 가 코사인 유사도
        conditions, params = [], [vec]

        if allowed_categories:
            conditions.append("cat_main = ANY(%s)")
            params.append(list(allowed_categories))

        if exclude_ids:
            conditions.append("id != ALL(%s)")
            params.append(list(exclude_ids))

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        params.append(vec)   # 정렬용
        params.append(top_k)

        sql = f"""
            SELECT
                title,
                author,
                cat_main,
                cat_mid,
                description,
                cover_url,
                link,
                popularity,
                -(embedding <#> %s) AS content_similarity
            FROM books
            {where_clause}
            ORDER BY embedding <#> %s
            LIMIT %s
        """

        start = time.perf_counter()
        with self._conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            cols = [d.name for d in cur.description]
        elapsed_ms = (time.perf_counter() - start) * 1000

        df = pd.DataFrame(rows, columns=cols)

        if df.empty:
            return df, {
                "filter_applied": bool(allowed_categories),
                "filter_relaxed": False,
                "allowed_categories": sorted(allowed_categories) if allowed_categories else [],
                "query_ms": round(elapsed_ms, 2),
            }

        # 하이브리드 스코어 (FAISS 경로와 동일한 계산)
        sim_min, sim_max = df["content_similarity"].min(), df["content_similarity"].max()
        if sim_max > sim_min:
            df["content_normalized"] = (df["content_similarity"] - sim_min) / (sim_max - sim_min)
        else:
            df["content_normalized"] = 1.0

        df["hybrid_score"] = (
            alpha * df["content_normalized"] + (1 - alpha) * df["popularity"]
        )
        df = df.sort_values("hybrid_score", ascending=False).reset_index(drop=True)

        meta = {
            "filter_applied": bool(allowed_categories),
            "filter_relaxed": False,   # WHERE 절 필터라 완화가 필요 없음
            "allowed_categories": sorted(allowed_categories) if allowed_categories else [],
            "query_ms": round(elapsed_ms, 2),
        }
        return df, meta

    def close(self):
        if self._conn and not self._conn.closed:
            self._conn.close()


    def find_by_title(self, keyword: str):
        """
        제목으로 도서를 찾아 저장된 임베딩 반환

        정규식은 인덱스를 타지 못해 전체 스캔이 발생하므로,
        파이썬에서 키워드를 정리한 뒤 ILIKE로만 조회한다.
        """
        import re
        # 부제·괄호 제거 후 핵심 키워드만 사용
        key = re.sub(r"[-–—]\s.*$", "", str(keyword))
        key = re.sub(r"[\(\[].*?[\)\]]", "", key).strip()
        if len(key) < 2:
            return None

        with self._conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, embedding FROM books
                WHERE title ILIKE %s
                ORDER BY popularity DESC
                LIMIT 1
            """, (f"%{key}%",))
            return cur.fetchone()

    def build_query_vector(self, queries, model):
        """
        입력에서 취향 벡터 생성

        DB에 있는 책은 저장된 임베딩을 쓰고(형식 일치),
        없는 책만 텍스트 인코딩으로 폴백한다.
        """
        vectors, matched_ids, matched_titles, unmatched = [], [], [], []

        for q in queries:
            row = self.find_by_title(q)
            if row:
                book_id, title, emb = row
                vectors.append(np.asarray(emb.to_list(), dtype=np.float32))
                matched_ids.append(book_id)
                matched_titles.append(title)
            else:
                vectors.append(
                    model.encode([q], convert_to_numpy=True,
                                 normalize_embeddings=True)[0]
                )
                unmatched.append(q)

        vec = np.mean(vectors, axis=0).astype(np.float32)
        n = np.linalg.norm(vec)
        if n > 0:
            vec /= n

        return vec, {
            "matched_count": len(matched_titles),
            "total_count": len(queries),
            "matched_titles": matched_titles,
            "matched_ids": matched_ids,
            "unmatched_queries": unmatched,
        }