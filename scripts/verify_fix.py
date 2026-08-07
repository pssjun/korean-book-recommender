import sys
sys.path.append(".")
import numpy as np, pandas as pd, faiss
from sentence_transformers import SentenceTransformer
from api.query_encoder import TitleMatcher, build_query_vector

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device="cpu")
books = pd.read_parquet("data/books_streamlit.parquet")
index = faiss.read_index("models/faiss_index.bin")
stored = np.asarray(index.reconstruct_n(0, index.ntotal), dtype=np.float32)
matcher = TitleMatcher(books, stored)

QUERIES = ["달러구트 꿈 백화점", "미드나잇 라이브러리", "불편한 편의점"]

def show(title, vec):
    sims, idxs = index.search(vec.astype(np.float32), 6)
    print(f"\n{title}")
    for r, (s, i) in enumerate(zip(sims[0], idxs[0]), 1):
        b = books.iloc[i]
        print(f"  {r}. [{b['cat_main']:12s}] {str(b['title'])[:34]:36s} {s:.4f}")

# Before
old = model.encode(QUERIES, convert_to_numpy=True, normalize_embeddings=True)
old = old.mean(axis=0, keepdims=True)
old /= np.linalg.norm(old)
show("[BEFORE] 텍스트 인코딩", old)

# After
new, meta = build_query_vector(QUERIES, matcher, model)
show("[AFTER] 저장 임베딩 활용", new)
print(f"\n매칭: {meta['matched_count']}/{meta['total_count']}")
if meta["unmatched_queries"]:
    print(f"미매칭: {meta['unmatched_queries']}")