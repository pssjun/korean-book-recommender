"""
PGVector 적재 스크립트

books_streamlit.parquet의 도서 메타데이터와 임베딩을 PostgreSQL에 적재한다.
FAISS와 동일한 모델·동일한 텍스트 구성을 사용해 결과를 비교할 수 있게 한다.

Usage:
    python scripts/load_pgvector.py
"""
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DIM = 384
DSN = os.getenv(
    "PG_DSN",
    "postgresql://bookuser:bookpass@localhost:5432/bookdb",
)

# FAISS 인덱스 생성 시와 동일한 텍스트 구성 (비교 가능성 확보)
def build_embedding_text(row) -> str:
    parts = [
        str(row.get("title") or ""),
        str(row.get("cat_mid") or ""),
        str(row.get("author_clean") or ""),
        str(row.get("description") or ""),
    ]
    return " . ".join(p for p in parts if p and p.lower() != "nan")


DDL = f"""
CREATE EXTENSION IF NOT EXISTS vector;

DROP TABLE IF EXISTS books;

CREATE TABLE books (
    id            SERIAL PRIMARY KEY,
    isbn13        TEXT,
    title         TEXT NOT NULL,
    author        TEXT,
    cat_main      TEXT,
    cat_mid       TEXT,
    publisher     TEXT,
    pub_date      TEXT,
    description   TEXT,
    cover_url     TEXT,
    link          TEXT,
    rating        REAL,
    popularity    REAL,
    embedding     vector({DIM})
);

-- 장르 필터용 인덱스 (FAISS에는 없던 기능)
CREATE INDEX idx_books_cat_main ON books (cat_main);
"""

# 벡터 인덱스는 데이터 적재 후 생성해야 효율적이다
VECTOR_INDEX = """
CREATE INDEX idx_books_embedding ON books
USING hnsw (embedding vector_ip_ops);
"""


def main():
    data_path = Path("data/books_streamlit.parquet")
    books = pd.read_parquet(data_path)
    print(f"[1/5] 도서 데이터 로드: {len(books):,}권")

    print(f"[2/5] 모델 로딩: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME, device="cpu")

    print("[3/5] 임베딩 생성 (수 분 소요)")
    texts = books.apply(build_embedding_text, axis=1).tolist()
    emb = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,   # 내적 = 코사인 유사도
    ).astype(np.float32)

    assert emb.shape == (len(books), DIM), f"임베딩 shape 불일치: {emb.shape}"

    print("[4/5] 테이블 생성 및 적재")
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
        conn.commit()
        register_vector(conn)

        start = time.time()
        with conn.cursor() as cur:
            with cur.copy(
                "COPY books (isbn13, title, author, cat_main, cat_mid, "
                "publisher, pub_date, description, cover_url, link, "
                "rating, popularity, embedding) FROM STDIN"
            ) as copy:
                for i, row in books.iterrows():
                    copy.write_row((
                        str(row.get("isbn13") or ""),
                        str(row["title"]),
                        str(row.get("author_clean") or ""),
                        str(row.get("cat_main") or ""),
                        str(row.get("cat_mid") or ""),
                        str(row.get("publisher") or ""),
                        str(row.get("pubDate") or ""),
                        str(row.get("description") or ""),
                        str(row.get("cover_url") or ""),
                        str(row.get("link") or ""),
                        float(row.get("rating") or 0),
                        float(row.get("popularity_score") or 0),
                        emb[i],
                    ))
        conn.commit()
        print(f"      적재 완료: {time.time() - start:.1f}s")

        print("[5/5] 벡터 인덱스 생성 (HNSW)")
        start = time.time()
        with conn.cursor() as cur:
            cur.execute(VECTOR_INDEX)
        conn.commit()
        print(f"      인덱스 생성 완료: {time.time() - start:.1f}s")

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM books")
            total = cur.fetchone()[0]
            cur.execute("SELECT COUNT(DISTINCT cat_main) FROM books")
            cats = cur.fetchone()[0]

    print()
    print("=" * 50)
    print(f"  도서 수    : {total:,}")
    print(f"  카테고리   : {cats}종")
    print(f"  벡터 차원  : {DIM}")
    print("=" * 50)


if __name__ == "__main__":
    main()