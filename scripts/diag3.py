import sys
sys.path.append(".")
import numpy as np, psycopg
from pgvector.psycopg import register_vector

conn = psycopg.connect("postgresql://bookuser:bookpass@localhost:5432/bookdb")
register_vector(conn)
cur = conn.cursor()

def search_by_title(keyword, top_k=5):
    """제목으로 책을 찾아 그 임베딩으로 유사 도서 검색"""
    cur.execute("""
        SELECT id, title, embedding FROM books
        WHERE title ILIKE %s ORDER BY popularity DESC LIMIT 1
    """, (f"%{keyword}%",))
    row = cur.fetchone()
    if not row:
        print(f"  '{keyword}' 매칭 실패")
        return
    book_id, title, emb = row
    print(f"\n기준 도서: {title[:40]}")
    cur.execute("""
        SELECT title, cat_main, -(embedding <#> %s) AS sim
        FROM books WHERE id != %s
        ORDER BY embedding <#> %s LIMIT %s
    """, (emb, book_id, emb, top_k))
    for i, (t, c, s) in enumerate(cur.fetchall(), 1):
        print(f"  {i}. [{c}] {t[:38]}  (sim={s:.4f})")

print("=" * 60)
print("저장된 임베딩 기반 검색")
print("=" * 60)
search_by_title("달러구트")
search_by_title("미드나잇 라이브러리")

conn.close()