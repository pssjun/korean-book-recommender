import sys
sys.path.append(".")

import numpy as np
import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DSN = "postgresql://bookuser:bookpass@localhost:5432/bookdb"

model = SentenceTransformer(MODEL, device="cpu")
conn = psycopg.connect(DSN)
register_vector(conn)
cur = conn.cursor()

# 1) DB 임베딩과 재생성 임베딩 비교
cur.execute("""
    SELECT title, cat_mid, author, description, embedding
    FROM books WHERE title LIKE '%달러구트%' LIMIT 1
""")
r = cur.fetchone()
title, cat_mid, author, desc, db_emb = r

txt = " . ".join(p for p in [title, cat_mid, author, desc] if p and p != "nan")
new_emb = model.encode([txt], normalize_embeddings=True)[0]
db_emb = np.array(db_emb.to_numpy() if hasattr(db_emb, "to_numpy") else db_emb, dtype=np.float32)

print("=" * 55)
print("1. 임베딩 일치 검사")
print("=" * 55)
print(f"  DB norm  : {np.linalg.norm(db_emb):.4f}   (1.0이어야 정규화됨)")
print(f"  New norm : {np.linalg.norm(new_emb):.4f}")
print(f"  cos sim  : {np.dot(db_emb, new_emb):.4f}   (0.99+ 면 동일)")

# 2) 책 1권으로 검색
print()
print("=" * 55)
print("2. 단일 책 검색 (달러구트)")
print("=" * 55)
q1 = model.encode(["달러구트 꿈 백화점"], normalize_embeddings=True)[0].astype(np.float32)
cur.execute("""
    SELECT title, cat_main, -(embedding <#> %s) AS sim
    FROM books ORDER BY embedding <#> %s LIMIT 5
""", (q1, q1))
for i, (t, c, s) in enumerate(cur.fetchall(), 1):
    print(f"  {i}. [{c}] {t[:35]}  (sim={s:.4f})")

# 3) 두 책 평균으로 검색
print()
print("=" * 55)
print("3. 두 책 평균 벡터 검색")
print("=" * 55)
embs = model.encode(
    ["달러구트 꿈 백화점", "미드나잇 라이브러리"],
    normalize_embeddings=True,
)
avg = embs.mean(axis=0)
avg = (avg / np.linalg.norm(avg)).astype(np.float32)
cur.execute("""
    SELECT title, cat_main, -(embedding <#> %s) AS sim
    FROM books ORDER BY embedding <#> %s LIMIT 5
""", (avg, avg))
for i, (t, c, s) in enumerate(cur.fetchall(), 1):
    print(f"  {i}. [{c}] {t[:35]}  (sim={s:.4f})")

conn.close()