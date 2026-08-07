# scripts/diag2.py
import sys, json
sys.path.append(".")
import numpy as np, pandas as pd, faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device="cpu")
books = pd.read_parquet("data/books_streamlit.parquet")
index = faiss.read_index("models/faiss_index.bin")

q = model.encode(["달러구트 꿈 백화점"], normalize_embeddings=True).astype(np.float32)
sims, idxs = index.search(q, 5)

print("FAISS 순수 유사도 결과")
for rank, (s, i) in enumerate(zip(sims[0], idxs[0]), 1):
    print(f"  {rank}. [{books.iloc[i]['cat_main']}] {books.iloc[i]['title'][:35]}  (sim={s:.4f})")