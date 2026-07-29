"""
FAISS 인덱스 재생성 스크립트

서빙에 사용하는 books parquet을 단일 기준(SSOT)으로 삼아 임베딩과 인덱스를
재생성한다. 이를 통해 도서 목록과 벡터 인덱스의 1:1 정합성을 보장한다.

Usage:
    python scripts/build_index.py
    python scripts/build_index.py --data data/books_streamlit.parquet --out models/faiss_index.bin
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def build_embedding_text(row) -> str:
    """임베딩 입력 텍스트 구성: 제목 . 카테고리 . 저자 . 소개문"""
    parts = [
        str(row.get("title") or ""),
        str(row.get("cat_mid") or ""),
        str(row.get("author_clean") or ""),
        str(row.get("description") or ""),
    ]
    return " . ".join([p for p in parts if p and p.lower() != "nan"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/books_streamlit.parquet")
    parser.add_argument("--out", default="models/faiss_index.bin")
    parser.add_argument("--batch-size", type=int, default=64)
    args = parser.parse_args()

    books = pd.read_parquet(args.data)
    print(f"[1/4] 도서 데이터 로드: {len(books):,}권")

    texts = books.apply(build_embedding_text, axis=1).tolist()
    empty_count = sum(1 for t in texts if not t.strip())
    if empty_count:
        print(f"      경고: 임베딩 텍스트가 비어있는 행 {empty_count}건")

    print(f"[2/4] 모델 로딩: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME, device="cpu")

    print(f"[3/4] 임베딩 생성 (CPU, 수 분 소요)")
    emb = model.encode(
        texts,
        batch_size=args.batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    print(f"      임베딩 shape: {emb.shape}")

    # 정합성 검증: 임베딩 행 수와 도서 수가 반드시 일치해야 함
    assert emb.shape[0] == len(books), (
        f"행 수 불일치: embeddings={emb.shape[0]}, books={len(books)}"
    )

    print("[4/4] FAISS 인덱스 생성 및 저장")
    index = faiss.IndexFlatIP(emb.shape[1])
    index.add(emb.astype(np.float32))

    assert index.ntotal == len(books), (
        f"인덱스 크기 불일치: index={index.ntotal}, books={len(books)}"
    )

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, args.out)

    print()
    print("=" * 50)
    print(f"완료: {args.out}")
    print(f"  도서 수 : {len(books):,}")
    print(f"  벡터 수 : {index.ntotal:,}")
    print(f"  차원    : {index.d}")
    print("=" * 50)


if __name__ == "__main__":
    main()