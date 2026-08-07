"""
API 요청/응답 데이터 모델 정의
Pydantic을 사용해 타입 검증과 자동 문서화를 동시에 처리
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class PathARequest(BaseModel):
    """Path A: 좋아하는 책 입력 기반 추천 요청"""
    books: List[str] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="좋아하는 책 제목 또는 설명 (1~5권)",
        examples=[["달러구트 꿈 백화점", "미드나잇 라이브러리", "불편한 편의점"]]
    )
    top_k: int = Field(default=10, ge=1, le=50, description="추천받을 도서 수")
    alpha: float = Field(
        default=0.7, ge=0.0, le=1.0,
        description="개인화 강도 (1.0=순수 콘텐츠, 0.0=순수 인기순)"
    )


class PathBRequest(BaseModel):
    """Path B: 태그 선택 기반 추천 요청"""
    tags: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="선택한 취향 태그",
        examples=[["소설", "힐링", "따뜻한"]]
    )
    top_k: int = Field(default=10, ge=1, le=50)
    alpha: float = Field(default=0.7, ge=0.0, le=1.0)


class BookItem(BaseModel):
    """추천 결과 도서 1건"""
    rank: int
    title: str
    author: str
    category_main: str
    category_mid: str
    content_similarity: float
    popularity_score: float
    hybrid_score: float
    cover_url: Optional[str] = None
    link: Optional[str] = None
    description: Optional[str] = None


class RecommendResponse(BaseModel):
    """추천 응답"""
    path: str = Field(description="사용된 추천 경로 (A 또는 B)")
    alpha: float
    query_summary: str
    total_books_searched: int
    elapsed_ms: float = Field(description="추천 처리 소요 시간(ms)")
    filter_applied: bool = Field(default=False, description="장르 카테고리 필터 적용 여부")
    filter_relaxed: bool = Field(default=False, description="필터 결과 부족으로 완화되었는지")
    allowed_categories: List[str] = Field(default_factory=list)
    results: List[BookItem]
    matched_count: int = Field(default=0, description="DB에서 찾은 입력 도서 수")
    total_count: int = Field(default=0, description="입력한 도서 수")
    unmatched_queries: List[str] = Field(default_factory=list, description="DB에 없는 입력")


class HealthResponse(BaseModel):
    """헬스체크 응답"""
    status: str
    model_loaded: bool
    index_size: int
    total_books: int
    llm_available: bool = Field(default=False, description="설명 생성 기능 사용 가능 여부")
    explanation_cache_size: int = Field(default=0)

class ExplainRequest(BaseModel):
    """추천 이유 설명 요청"""
    query_summary: str = Field(..., description="사용자 입력 요약 (책 목록 또는 태그)")
    path: str = Field(..., pattern="^[AB]$", description="추천 경로 (A 또는 B)")
    books: List[dict] = Field(
        ..., min_length=1, max_length=10,
        description="추천된 도서 목록 (rank, title, author, category, similarity, description)"
    )


class ExplainResponse(BaseModel):
    """추천 이유 설명 응답"""
    explanation: Optional[str] = Field(None, description="LLM이 생성한 설명 (실패 시 null)")
    available: bool = Field(description="LLM 기능 사용 가능 여부")
    model: Optional[str] = Field(None, description="사용된 모델 ID")
    cached: bool = Field(description="캐시에서 반환되었는지")
    elapsed_ms: float
    error: Optional[str] = None