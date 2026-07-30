"""
RAG 기반 추천 이유 설명 생성

구조:
  Retrieval  : FAISS로 검색된 도서 (기존 추천 파이프라인)
  Augmented  : 검색된 도서 메타데이터를 컨텍스트로 구성
  Generation : LLM이 추천 근거를 자연어로 설명

설계 원칙:
  - LLM 실패가 추천 실패로 이어지지 않도록 폴백 (설명 없이 추천만 반환)
  - 외부 공급자의 모델 지원 중단에 대응하는 모델 폴백 체인
  - 동일 입력 반복 호출을 캐싱해 지연·비용·rate limit 완화
  - 컨텍스트에 실제 도서 메타데이터만 포함해 환각 억제
"""
import os
import time
import logging
import hashlib
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False

# 모델 후보 (앞에서부터 시도)
# 공급자 측 모델 지원 중단 이력이 있어 폴백 체인으로 구성
MODEL_CANDIDATES = [
    os.getenv("GEMINI_MODEL"),      # 환경 변수로 우선 지정 가능
    "gemini-flash-lite-latest",     # 별칭: 항상 최신 Flash-Lite
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
]
MODEL_CANDIDATES = [m for m in MODEL_CANDIDATES if m]

MAX_DESC_CHARS = 300        # 도서당 소개문 최대 길이 (컨텍스트 절약)
MAX_BOOKS_IN_CONTEXT = 5    # 컨텍스트에 포함할 도서 수
REQUEST_TIMEOUT_MS = 15_000


class RecommendationExplainer:
    """추천 결과에 대한 설명을 LLM으로 생성"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self._client = None
        self.model_name: Optional[str] = None
        self._available = False

        if not _GENAI_AVAILABLE:
            logger.warning("google-genai not installed - explanation disabled")
            return

        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not set - explanation disabled")
            return

        try:
            client = genai.Client(
                api_key=self.api_key,
                http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS),
            )

            # 후보 모델을 순서대로 실제 호출해 사용 가능한 첫 모델을 채택
            # (객체 생성만으로는 모델 가용성을 알 수 없어 실호출로 검증)
            last_error = None
            for model_name in MODEL_CANDIDATES:
                try:
                    client.models.generate_content(
                        model=model_name,
                        contents="ok",
                        config=types.GenerateContentConfig(max_output_tokens=5),
                    )
                    self._client = client
                    self.model_name = model_name
                    self._available = True
                    logger.info(f"Explainer initialized with {model_name}")
                    break
                except Exception as e:
                    last_error = e
                    logger.warning(f"Model {model_name} unavailable: {e}")
                    continue

            if not self._available:
                logger.warning(f"All model candidates failed. Last error: {last_error}")

        except Exception as e:
            logger.warning(f"Failed to initialize explainer: {e}")

    @property
    def is_available(self) -> bool:
        return self._available

    def _build_context(self, query_summary: str, books: List[Dict], path: str) -> str:
        """검색된 도서 메타데이터로 컨텍스트 구성 (환각 억제)"""
        input_label = "좋아하는 책" if path == "A" else "선택한 취향 태그"

        lines = [f"[사용자 {input_label}]", query_summary, "", "[추천된 도서 목록]"]

        for b in books[:MAX_BOOKS_IN_CONTEXT]:
            desc = (b.get("description") or "")[:MAX_DESC_CHARS]
            lines.append(
                f"{b['rank']}. 《{b['title']}》 / {b.get('author', '저자 미상')}\n"
                f"   분류: {b.get('category_main', '')} > {b.get('category_mid', '')}\n"
                f"   유사도: {b['content_similarity']:.3f}\n"
                f"   소개: {desc}"
            )

        return "\n".join(lines)

    def _build_prompt(self, context: str, path: str) -> str:
        input_label = "입력한 책들" if path == "A" else "선택한 태그"

        return f"""당신은 도서 큐레이터입니다. 아래 추천 결과를 독자에게 설명해주세요.

{context}


[출력 형식]

**전체 추천 방향**
사용자의 {input_label}과 추천 도서 전반의 공통점을 2~3문장으로 설명하세요.

**개별 도서**
상위 3권에 대해 각각 아래 형식으로 작성하세요.

《도서명》
- 어떤 책인가: 소개문을 바탕으로 이 책이 다루는 내용을 2문장으로 정리
- 분위기: 소개문에서 읽히는 정서와 톤을 1문장으로 (예: 담담하지만 여운이 남는, 유쾌하고 경쾌한)
- 추천 이유: 사용자의 {input_label}과 어떤 지점에서 연결되는지 1~2문장

[작성 규칙]
1. 위에 제공된 소개문에 근거해서만 작성하세요. 줄거리를 추측하거나 없는 내용을 만들지 마세요.
2. 소개문이 짧아 내용 파악이 어려운 책은 "소개 정보가 제한적이다"라고 명시하고, 확인 가능한 범위(장르, 분류)만 언급하세요.
3. 유사도 수치는 직접 언급하지 마세요.
4. 문체는 서점 큐레이션처럼 자연스럽게 작성하세요."""

    def explain(self, query_summary: str, books: List[Dict], path: str) -> Dict:
        """
        추천 이유 설명 생성 (실패해도 예외를 던지지 않음)

        Returns:
            explanation, available, model, elapsed_ms, cached, error
        """
        if not self._available:
            return {
                "explanation": None,
                "available": False,
                "model": None,
                "elapsed_ms": 0.0,
                "cached": False,
                "error": "LLM not configured",
            }

        # 캐시 키: 모델이 바뀌면 설명도 달라지므로 모델명 포함
        cache_key = hashlib.md5(
            f"{self.model_name}|{path}|{query_summary}|"
            f"{'|'.join(b['title'] for b in books[:MAX_BOOKS_IN_CONTEXT])}".encode()
        ).hexdigest()

        cached = _get_cached_explanation(cache_key)
        if cached:
            return {
                "explanation": cached,
                "available": True,
                "model": self.model_name,
                "elapsed_ms": 0.0,
                "cached": True,
                "error": None,
            }

        start = time.perf_counter()
        try:
            context = self._build_context(query_summary, books, path)
            prompt = self._build_prompt(context, path)

            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,        # 낮게 유지해 환각 억제
                    max_output_tokens=1200,
                ),
            )

            text = (response.text or "").strip()
            elapsed_ms = (time.perf_counter() - start) * 1000

            if not text:
                raise ValueError("Empty response from LLM")

            _set_cached_explanation(cache_key, text)
            logger.info(f"Explanation generated in {elapsed_ms:.0f}ms ({self.model_name})")

            return {
                "explanation": text,
                "available": True,
                "model": self.model_name,
                "elapsed_ms": round(elapsed_ms, 2),
                "cached": False,
                "error": None,
            }

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.warning(f"Explanation failed after {elapsed_ms:.0f}ms: {e}")
            return {
                "explanation": None,
                "available": True,
                "model": self.model_name,
                "elapsed_ms": round(elapsed_ms, 2),
                "cached": False,
                "error": str(e),
            }


# ---- 인메모리 캐시 ----
# 프로덕션에서는 Redis 등 외부 캐시로 교체
_explanation_cache: Dict[str, str] = {}
_CACHE_MAX_SIZE = 500


def _get_cached_explanation(key: str) -> Optional[str]:
    return _explanation_cache.get(key)


def _set_cached_explanation(key: str, value: str) -> None:
    if len(_explanation_cache) >= _CACHE_MAX_SIZE:
        _explanation_cache.pop(next(iter(_explanation_cache)))  # FIFO
    _explanation_cache[key] = value


def get_cache_stats() -> Dict:
    return {"size": len(_explanation_cache), "max_size": _CACHE_MAX_SIZE}