<<<<<<< HEAD
=======
"""
한국 도서 하이브리드 추천 시스템 - 홈 페이지
"""
import streamlit as st
import json
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="한국 도서 추천 시스템",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 설정 로드
@st.cache_data
def load_config():
    config_path = Path("data/config.json")
    if not config_path.exists():
        return {
            "total_books": 6974,
            "embedding_model": "jhgan/ko-sroberta-multitask",
            "default_alpha": 0.7,
            "default_top_k": 10,
            "project_meta": {
                "name": "한국 도서 하이브리드 추천 시스템",
                "phase": "Portfolio v1.0"
            }
        }
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()

# =========================
# 상단 헤더
# =========================
st.title("📚 한국 도서 하이브리드 추천 시스템")
st.markdown("### 알라딘 API + SentenceBERT + FAISS 기반 개인화 도서 추천")

st.divider()

# =========================
# 프로젝트 요약 카드
# =========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("한국 도서", f"{config['total_books']:,}권", help="알라딘 API로 수집")
with col2:
    st.metric("임베딩 모델", "ko-sroberta", help="한국어 특화 SentenceBERT")
with col3:
    st.metric("벡터 차원", "768", help="임베딩 벡터 크기")
with col4:
    st.metric("CF 벤치마크", "6종 모델", help="Baseline 3 + MF 2 + NCF 1")

st.divider()

# =========================
# 문제 정의
# =========================
st.header("🎯 문제 정의")

st.markdown("""
국내 대형 서점(교보문고, 알라딘, YES24)의 추천 시스템은 대부분 **판매량·조회수 기반의 인기 순위**에 의존한다.  
독자의 개별 취향과 문맥을 반영한 개인화 추천은 미흡한 실정이며,  
특히 **신규 이용자를 위한 취향 파악 온보딩 과정이 부재**하여 첫 진입 시점부터 개인화 경험을 제공받지 못한다.

**본 프로젝트는 다음을 해결한다:**

1. 신규 유저 첫 진입 시점의 즉시 개인화
2. 국내 도서 유저-상호작용 데이터 부재라는 현실적 제약 극복
3. 콘텐츠 기반 + 협업 필터링의 하이브리드 접근으로 롱테일 도서 발굴
""")

st.divider()

# =========================
# 시스템 아키텍처
# =========================
st.header("🏗️ 시스템 아키텍처")

st.markdown("""
### 이중 트랙 설계

**트랙 1: 콘텐츠 임베딩 (알라딘 + SentenceBERT + FAISS)**  
실제 한국 도서 추천을 담당. 도서 소개문·저자·카테고리를 SentenceBERT로 임베딩하고 FAISS로 유사도 검색.

**트랙 2: 협업 필터링 (Book-Crossing 벤치마크)**  
방법론 검증. Baseline 3종(Popularity, User-CF, Item-CF) + Matrix Factorization 2종(SVD, ALS) + Neural CF 실험.

**하이브리드 결합**
최종 점수 = α × 콘텐츠_유사도 + (1 − α) × 인기 신호
α 파라미터로 개인화 강도 조절.
""")

st.divider()

# =========================
# 페이지 안내
# =========================
st.header("🗺️ 페이지 안내")

st.markdown("""
좌측 사이드바에서 다음 페이지로 이동할 수 있습니다 (추가 예정):

- **📖 책 추천받기** — 좋아하는 책 또는 태그로 즉시 개인화 추천
- **📊 협업 필터링 실험** — 6종 CF 모델 성능 비교 및 인사이트
- **🧪 시스템 분석** — 하이브리드 아키텍처 및 α 파라미터 실험
- **📝 결론과 한계** — 프로젝트 회고 및 향후 개선 방향
""")

st.divider()

# 하단 여백
st.write("")
st.caption("💡 브라우저 자동 번역 기능이 켜져 있으면 UI가 왜곡될 수 있습니다. '원본 보기'로 설정해주세요.")
>>>>>>> 20ab405 (Add book recommendation page)
