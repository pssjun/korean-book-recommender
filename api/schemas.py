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


class RecommendResponse(BaseModel):
    """추천 응답"""
    path: str = Field(description="사용된 추천 경로 (A 또는 B)")
    alpha: float
    query_summary: str
    total_books_searched: int
    elapsed_ms: float = Field(description="추천 처리 소요 시간(ms)")
    results: List[BookItem]


class HealthResponse(BaseModel):
    """헬스체크 응답"""
    status: str
    model_loaded: bool
    index_size: int
    total_books: int