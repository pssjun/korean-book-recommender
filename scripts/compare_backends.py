"""
FAISS vs PGVector 비교

같은 쿼리에 대해 두 백엔드의 결과와 속도를 비교한다.
특히 장르 필터 동작 방식의 차이를 확인한다.
"""
import sys
import time

import numpy as np
from sentence_transformers import SentenceTransformer

sys.path.append(".")
from api.genre_filter import resolve_allowed_categories
from api.pgvector_search import PgVectorSearcher

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def encode(model, texts):
    emb = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    vec = emb.mean(axis=0, keepdims=True).astype(np.float32)
    vec /= np.linalg.norm(vec)
    return vec


def main():
    print("모델 로딩...")
    model = SentenceTransformer(MODEL_NAME, device="cpu")

    print("PGVector 연결...")
    pg = PgVectorSearcher()
    pg.connect()
    print(f"  적재된 도서: {pg.count():,}권\n")

    # ---- 케이스 1: 필터 없음 ----
    print("=" * 60)
    print("케이스 1 — 필터 없음 (좋아하는 책 기반)")
    print("=" * 60)
    query = ["달러구트 꿈 백화점", "미드나잇 라이브러리", "불편한 편의점"]

    vec, mmeta = pg.build_query_vector(query, model)
    print(f"제목 매칭: {mmeta['matched_count']}/{mmeta['total_count']}")
    if mmeta["unmatched_queries"]:
        print(f"  미매칭: {mmeta['unmatched_queries']}")

    df, meta = pg.search(vec, top_k=5, alpha=0.7, exclude_ids=mmeta["matched_ids"])
    print(f"쿼리 시간: {meta['query_ms']}ms")
    for i, row in df.iterrows():
        print(f"  {i+1}. [{row['cat_main']}] {row['title'][:35]}")

    # ---- 케이스 2: 장르 필터 ----
    print()
    print("=" * 60)
    print("케이스 2 — 장르 필터 (소설)")
    print("=" * 60)
    tags = ["소설", "힐링"]
    allowed = resolve_allowed_categories(tags)
    print(f"허용 카테고리: {sorted(allowed)}")

    vec2 = encode(model, ["소설, 스토리, 등장인물 . 따뜻한 이야기, 위로, 힐링"])
    df2, meta2 = pg.search(vec2, top_k=5, alpha=0.7, allowed_categories=allowed)
    print(f"쿼리 시간: {meta2['query_ms']}ms")
    for i, row in df2.iterrows():
        print(f"  {i+1}. [{row['cat_main']}] {row['title']}")

    # 필터 검증
    outside = df2[~df2["cat_main"].isin(allowed)]
    print()
    print(f"허용 범위 밖 결과: {len(outside)}건", "✅" if len(outside) == 0 else "❌")

    # ---- 케이스 3: 반복 측정 ----
    print()
    print("=" * 60)
    print("케이스 3 — 쿼리 속도 (10회 평균)")
    print("=" * 60)
    times = []
    for _ in range(10):
        _, m = pg.search(vec, top_k=10, alpha=0.7)
        times.append(m["query_ms"])
    print(f"  평균: {np.mean(times):.2f}ms")
    print(f"  최소: {np.min(times):.2f}ms / 최대: {np.max(times):.2f}ms")

    pg.close()


if __name__ == "__main__":
    main()