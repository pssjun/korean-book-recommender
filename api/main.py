"""
한국 도서 하이브리드 추천 API
- FastAPI 기반 모델 서빙
- 앱 시작 시 모델을 1회 로딩해 메모리에 상주 (요청당 재로딩 방지)
"""
import time
import logging
from contextlib import asynccontextmanager

# .env 파일을 환경 변수로 로딩 (로컬 개발 편의)
# 컨테이너 환경에서는 파일이 없으므로 무시됨
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .recommender import HybridRecommender
from .schemas import (
    PathARequest, PathBRequest, RecommendResponse, BookItem, HealthResponse
)
from .explainer import RecommendationExplainer, get_cache_stats
from .schemas import (
    PathARequest, PathBRequest, RecommendResponse, BookItem, HealthResponse,
    ExplainRequest, ExplainResponse
)

recommender = HybridRecommender()
explainer = RecommendationExplainer()


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
                description=str(row["description"])[:300] if row.get("description") else None,
            )
        )
    return items


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """헬스체크 - 모델 로딩 상태, 데이터 정합성, LLM 사용 가능 여부"""
    cache = get_cache_stats()
    return HealthResponse(
        status="ok" if recommender.is_loaded else "loading",
        model_loaded=recommender.is_loaded,
        index_size=recommender.faiss_index.ntotal if recommender.is_loaded else 0,
        total_books=len(recommender.books) if recommender.is_loaded else 0,
        llm_available=explainer.is_available,
        explanation_cache_size=cache["size"],
    )


@app.post("/recommend/path-a", response_model=RecommendResponse, tags=["Recommend"])
def recommend_path_a(req: PathARequest):
    """Path A: 좋아하는 책을 입력받아 유사한 한국 도서 추천"""
    if not recommender.is_loaded:
        raise HTTPException(status_code=503, detail="Model is still loading")

    try:
        results, elapsed_ms, meta = recommender.recommend_path_a(
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
        filter_applied=meta["filter_applied"],
        filter_relaxed=meta["filter_relaxed"],
        allowed_categories=meta["allowed_categories"],
        results=_to_book_items(results),
    )


@app.post("/recommend/path-b", response_model=RecommendResponse, tags=["Recommend"])
def recommend_path_b(req: PathBRequest):
    """
    Path B: 취향 태그를 입력받아 매칭되는 한국 도서 추천

    장르 태그(소설, 에세이 등)는 임베딩 검색과 함께 카테고리 필터로도 작동합니다.
    분위기 태그(따뜻한, 묵직한 등)는 필터 없이 임베딩에만 반영됩니다.
    """
    if not recommender.is_loaded:
        raise HTTPException(status_code=503, detail="Model is still loading")

    try:
        results, elapsed_ms, meta = recommender.recommend_path_b(
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
        filter_applied=meta["filter_applied"],
        filter_relaxed=meta["filter_relaxed"],
        allowed_categories=meta["allowed_categories"],
        results=_to_book_items(results),
    )

@app.get("/tags", tags=["Recommend"])
def list_tags():
    """사용 가능한 취향 태그 목록 조회"""
    if not recommender.is_loaded:
        raise HTTPException(status_code=503, detail="Model is still loading")
    return {"tags": list(recommender.tag_templates.keys())}

@app.post("/explain", response_model=ExplainResponse, tags=["Explain"])
def explain_recommendation(req: ExplainRequest):
    """
    RAG 기반 추천 이유 설명 생성

    추천 결과의 도서 메타데이터를 컨텍스트로 구성하여 LLM이 추천 근거를
    자연어로 설명합니다.

    - LLM 호출 실패 시에도 200을 반환하며 `explanation`이 null이 됩니다
      (설명은 부가 기능이므로 추천 흐름을 중단시키지 않음)
    - 동일 입력 조합은 캐시에서 반환됩니다
    """
    result = explainer.explain(
        query_summary=req.query_summary,
        books=req.books,
        path=req.path,
    )
    return ExplainResponse(**result)