
"""
하이브리드 추천 시스템 - Streamlit용 재사용 모듈
"""
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer


class HybridRecommender:
    def __init__(self, config, books_df, faiss_index, sbert_model, tag_templates):
        self.config = config
        self.books = books_df
        self.faiss_index = faiss_index
        self.sbert = sbert_model
        self.tag_templates = tag_templates

    def path_a(self, book_queries, top_k=None):
        """Path A: 주관식 - 좋아하는 책 텍스트"""
        top_k = top_k or self.config["default_top_k"]

        embeds = self.sbert.encode(
            book_queries,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        user_vector = embeds.mean(axis=0, keepdims=True).astype(np.float32)
        user_vector /= np.linalg.norm(user_vector)

        search_k = top_k * 3
        sims, indices = self.faiss_index.search(user_vector, search_k)

        results = self.books.iloc[indices[0]].copy()
        results["content_similarity"] = sims[0]
        return results.reset_index(drop=True)

    def path_b(self, selected_tags, top_k=None):
        """Path B: 객관식 - 태그 조합"""
        top_k = top_k or self.config["default_top_k"]

        tag_texts = [self.tag_templates.get(t, t) for t in selected_tags]
        combined = " . ".join(tag_texts)

        embed = self.sbert.encode(
            [combined],
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype(np.float32)

        search_k = top_k * 3
        sims, indices = self.faiss_index.search(embed, search_k)

        results = self.books.iloc[indices[0]].copy()
        results["content_similarity"] = sims[0]
        return results.reset_index(drop=True)

    def hybrid(self, book_queries=None, selected_tags=None, top_k=None, alpha=None):
        """하이브리드 추천 (콘텐츠 + 인기 결합)"""
        top_k = top_k or self.config["default_top_k"]
        alpha = alpha if alpha is not None else self.config["default_alpha"]

        if book_queries:
            candidates = self.path_a(book_queries, top_k=top_k)
            path = "A"
        elif selected_tags:
            candidates = self.path_b(selected_tags, top_k=top_k)
            path = "B"
        else:
            raise ValueError("book_queries 또는 selected_tags 필요")

        # 유사도 정규화
        sim_min = candidates["content_similarity"].min()
        sim_max = candidates["content_similarity"].max()
        if sim_max > sim_min:
            candidates["content_normalized"] = (
                (candidates["content_similarity"] - sim_min) / (sim_max - sim_min)
            )
        else:
            candidates["content_normalized"] = 1.0

        # 하이브리드 점수
        candidates["hybrid_score"] = (
            alpha * candidates["content_normalized"] +
            (1 - alpha) * candidates["popularity_score"]
        )

        # 정렬
        candidates = candidates.sort_values("hybrid_score", ascending=False).head(top_k)
        candidates = candidates.reset_index(drop=True)
        candidates.index = range(1, len(candidates) + 1)

        return {
            "path": path,
            "alpha": alpha,
            "results": candidates
        }
