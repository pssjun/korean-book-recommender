"""
한국 도서 하이브리드 추천 API
- FastAPI 기반 모델 서빙
- 앱 시작 시 모델을 1회 로딩해 메모리에 상주 (요청당 재로딩 방지)
"""
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .recommender import HybridRecommender
from .schemas import (
    PathARequest, PathBRequest, RecommendResponse, BookItem, HealthResponse
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

recommender = HybridRecommender()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작 시 모델 로딩, 종료 시 정리"""
    recommender.load()
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Korean Book Hybrid Recommender API",
    description="콘텐츠 임베딩(SentenceBERT+FAISS)과 인기 신호를 결합한 한국 도서 추천 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """요청 로깅 + 응답시간 측정 (모니터링 기초)"""
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info(
        f"{request.method} {request.url.path} "
        f"| status={response.status_code} | {elapsed_ms:.1f}ms"
    )
    response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.1f}"
    return response


def _to_book_items(results_df) -> list:
    """DataFrame을 응답 스키마로 변환"""
    items = []
    for i, row in results_df.iterrows():
        items.append(
            BookItem(
                rank=i + 1,
                title=str(row["title"]),
                author=str(row.get("author_clean", "")),
                category_main=str(row.get("cat_main", "")),
                category_mid=str(row.get("cat_mid", "")),
                content_similarity=float(row["content_similarity"]),
                popularity_score=float(row["popularity_score"]),
                hybrid_score=float(row["hybrid_score"]),
                cover_url=str(row["cover_url"]) if row.get("cover_url") else None,
                link=str(row["link"]) if row.get("link") else None,
            )
        )
    return items


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """헬스체크 - 컨테이너 오케스트레이션 및 모니터링용"""
    return HealthResponse(
        status="ok" if recommender.is_loaded else "loading",
        model_loaded=recommender.is_loaded,
        index_size=recommender.faiss_index.ntotal if recommender.is_loaded else 0,
        total_books=len(recommender.books) if recommender.is_loaded else 0,
    )


@app.post("/recommend/path-a", response_model=RecommendResponse, tags=["Recommend"])
def recommend_path_a(req: PathARequest):
    """
    Path A: 좋아하는 책을 입력받아 유사한 한국 도서 추천

    입력한 책들의 임베딩을 평균내어 취향 벡터를 만들고,
    FAISS로 유사 도서를 검색한 뒤 인기 신호와 결합합니다.
    """
    if not recommender.is_loaded:
        raise HTTPException(status_code=503, detail="Model is still loading")

    try:
        results, elapsed_ms = recommender.recommend_path_a(
            books=req.books, top_k=req.top_k, alpha=req.alpha
        )
    except Exception as e:
        logger.exception("Recommendation failed")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {e}")

    return RecommendResponse(
        path="A",
        alpha=req.alpha,
        query_summary=", ".join(req.books),
        total_books_searched=recommender.faiss_index.ntotal,
        elapsed_ms=round(elapsed_ms, 2),
        results=_to_book_items(results),
    )


@app.post("/recommend/path-b", response_model=RecommendResponse, tags=["Recommend"])
def recommend_path_b(req: PathBRequest):
    """
    Path B: 취향 태그를 입력받아 매칭되는 한국 도서 추천

    태그를 자연어로 변환한 뒤 임베딩하여 동일한 검색 로직을 사용합니다.
    신규 유저의 콜드 스타트 상황에 대응합니다.
    """
    if not recommender.is_loaded:
        raise HTTPException(status_code=503, detail="Model is still loading")

    try:
        results, elapsed_ms = recommender.recommend_path_b(
            tags=req.tags, top_k=req.top_k, alpha=req.alpha
        )
    except Exception as e:
        logger.exception("Recommendation failed")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {e}")

    return RecommendResponse(
        path="B",
        alpha=req.alpha,
        query_summary=", ".join(req.tags),
        total_books_searched=recommender.faiss_index.ntotal,
        elapsed_ms=round(elapsed_ms, 2),
        results=_to_book_items(results),
    )


@app.get("/tags", tags=["Recommend"])
def list_tags():
    """사용 가능한 취향 태그 목록 조회"""
    if not recommender.is_loaded:
        raise HTTPException(status_code=503, detail="Model is still loading")
    return {"tags": list(recommender.tag_templates.keys())}