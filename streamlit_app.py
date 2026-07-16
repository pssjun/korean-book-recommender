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

# 브라우저 자동 번역 방지
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# =========================
# 설정 로드
# =========================
@st.cache_data
def load_config():
    config_path = Path("data/config.json")
    if not config_path.exists():
        return {
            "total_books": 6974,
            "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
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
# 커스텀 CSS
# =========================
st.markdown("""
<style>
/* 히어로 섹션 */
.hero {
    background: linear-gradient(135deg, #1E3A5F 0%, #2E86AB 50%, #4A9FD1 100%);
    padding: 50px 40px;
    border-radius: 20px;
    margin-bottom: 30px;
    color: white;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}
.hero-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 12px;
    color: white;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    font-size: 18px;
    opacity: 0.9;
    margin-bottom: 20px;
    font-weight: 400;
}
.hero-tags {
    display: flex;
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 20px;
}
.hero-tag {
    background: rgba(255,255,255,0.15);
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
}

/* 통계 카드 */
.stat-card {
    background: linear-gradient(145deg, #1E1E2E, #2A2A3E);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.08);
    transition: all 0.3s ease;
    height: 100%;
}
.stat-card:hover {
    transform: translateY(-4px);
    border: 1px solid rgba(74, 159, 209, 0.4);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}
.stat-icon {
    font-size: 32px;
    margin-bottom: 12px;
}
.stat-value {
    font-size: 28px;
    font-weight: 700;
    color: #4A9FD1;
    margin-bottom: 4px;
}
.stat-label {
    font-size: 13px;
    color: #A0A0B0;
    font-weight: 500;
}

/* 섹션 헤더 */
.section-header {
    font-size: 26px;
    font-weight: 700;
    margin: 40px 0 20px 0;
    padding-left: 12px;
    border-left: 4px solid #4A9FD1;
}

/* 문제 정의 카드 */
.problem-card {
    background: linear-gradient(145deg, #1E1E2E, #2A2A3E);
    border-radius: 16px;
    padding: 30px;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 20px;
}
.problem-title {
    font-size: 18px;
    font-weight: 700;
    color: #F5B041;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.problem-body {
    color: #D0D0DA;
    line-height: 1.7;
    font-size: 14px;
}

/* 아키텍처 다이어그램 */
.arch-container {
    background: linear-gradient(145deg, #1E1E2E, #2A2A3E);
    border-radius: 20px;
    padding: 40px 30px;
    border: 1px solid rgba(255,255,255,0.08);
    margin: 20px 0;
}
.arch-track {
    display: flex;
    gap: 20px;
    margin-bottom: 25px;
}
.arch-box {
    flex: 1;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    transition: all 0.3s;
}
.arch-box:hover {
    transform: scale(1.02);
}
.arch-box-content {
    background: rgba(46, 134, 171, 0.1);
    border: 2px solid rgba(46, 134, 171, 0.4);
}
.arch-box-cf {
    background: rgba(243, 156, 18, 0.1);
    border: 2px solid rgba(243, 156, 18, 0.4);
}
.arch-box-hybrid {
    background: rgba(46, 204, 113, 0.15);
    border: 2px solid rgba(46, 204, 113, 0.5);
}
.arch-box-title {
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 8px;
    color: white;
}
.arch-box-desc {
    font-size: 12px;
    color: #C0C0D0;
    line-height: 1.5;
}
.arch-arrow {
    text-align: center;
    color: #4A9FD1;
    font-size: 28px;
    margin: 8px 0;
}
.arch-formula {
    background: rgba(46, 204, 113, 0.08);
    border: 1px dashed rgba(46, 204, 113, 0.5);
    border-radius: 8px;
    padding: 16px;
    text-align: center;
    color: #2ECC71;
    font-family: 'Courier New', monospace;
    font-size: 15px;
    font-weight: 600;
    margin-top: 20px;
}

/* 페이지 안내 카드 */
.page-card {
    background: linear-gradient(145deg, #1E1E2E, #2A2A3E);
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(255,255,255,0.08);
    height: 100%;
    transition: all 0.3s ease;
    cursor: pointer;
}
.page-card:hover {
    transform: translateY(-4px);
    border: 1px solid rgba(74, 159, 209, 0.4);
    box-shadow: 0 8px 24px rgba(74, 159, 209, 0.15);
}
.page-icon {
    font-size: 40px;
    margin-bottom: 12px;
}
.page-title {
    font-size: 17px;
    font-weight: 700;
    color: white;
    margin-bottom: 8px;
}
.page-desc {
    font-size: 13px;
    color: #A0A0B0;
    line-height: 1.6;
}

/* 기술 스택 */
.tech-badge {
    display: inline-block;
    padding: 6px 14px;
    background: rgba(74, 159, 209, 0.15);
    border: 1px solid rgba(74, 159, 209, 0.3);
    color: #4A9FD1;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    margin: 4px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 히어로 섹션
# =========================
st.markdown(f"""
<div class="hero">
    <div class="hero-title">📚 한국 도서 하이브리드 추천 시스템</div>
    <div class="hero-subtitle">
        국내 서점의 획일화된 인기순 추천을 넘어,<br>
        <b>취향 기반 개인화 도서 발견</b>을 지원하는 하이브리드 추천 엔진
    </div>
    <div class="hero-tags">
        <span class="hero-tag">🎯 개인화 추천</span>
        <span class="hero-tag">🧠 SentenceBERT</span>
        <span class="hero-tag">⚡ FAISS</span>
        <span class="hero-tag">🔬 협업 필터링</span>
        <span class="hero-tag">🎨 하이브리드</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 통계 카드
# =========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon">📚</div>
        <div class="stat-value">{config['total_books']:,}</div>
        <div class="stat-label">한국 도서 (알라딘)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-icon">🧠</div>
        <div class="stat-value">384-D</div>
        <div class="stat-label">임베딩 벡터 차원</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-icon">🔬</div>
        <div class="stat-value">6종</div>
        <div class="stat-label">CF 벤치마크 모델</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-icon">⚡</div>
        <div class="stat-value">&lt;100ms</div>
        <div class="stat-label">검색 응답 시간</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 빠른 시작 CTA
# =========================
st.markdown("<div class='section-header'>🚀 지금 바로 추천받기</div>", unsafe_allow_html=True)

cta_col1, cta_col2, cta_col3 = st.columns([1, 2, 1])
with cta_col2:
    st.info("👈 좌측 사이드바의 **책 추천받기** 메뉴에서 시작하세요")
    st.caption("좋아하는 책 3권을 입력하거나, 취향 태그를 선택하시면 즉시 유사한 한국 도서를 추천해드립니다.")

# =========================
# 문제 정의
# =========================
st.markdown("<div class='section-header'>🎯 왜 이 프로젝트를 만들었나요?</div>", unsafe_allow_html=True)

prob_col1, prob_col2 = st.columns(2)

with prob_col1:
    st.markdown("""
    <div class="problem-card">
        <div class="problem-title">
            <span>😕</span>
            <span>국내 서점의 획일화된 추천</span>
        </div>
        <div class="problem-body">
            교보문고, 알라딘, YES24 등 대형 서점의 추천 시스템은 대부분<br>
            <b>판매량·조회수 기반의 인기 순위</b>에 의존합니다.<br><br>
            독자의 개별 취향과 문맥을 반영한 개인화는 미흡하며,<br>
            신규 이용자를 위한 <b>온보딩 과정이 부재</b>합니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

with prob_col2:
    st.markdown("""
    <div class="problem-card">
        <div class="problem-title">
            <span>💡</span>
            <span>본 프로젝트가 해결하는 것</span>
        </div>
        <div class="problem-body">
            ✅ <b>신규 유저 첫 진입 시점</b>부터 즉시 개인화<br>
            ✅ <b>유저-상호작용 데이터 부재</b> 라는 현실적 제약 극복<br>
            ✅ <b>콘텐츠 + 협업 필터링 하이브리드</b>로 롱테일 도서 발굴<br>
            ✅ α 파라미터로 <b>개인화 강도 유연 조절</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 시스템 아키텍처
# =========================
st.markdown("<div class='section-header'>🏗️ 시스템 아키텍처</div>", unsafe_allow_html=True)

st.markdown("""
<div class="arch-container">
    <div class="arch-track">
        <div class="arch-box arch-box-content">
            <div class="arch-box-title">🎯 트랙 1: 콘텐츠 임베딩</div>
            <div class="arch-box-desc">
                알라딘 API로 수집한 6,974권 한국 도서<br>
                SentenceBERT로 벡터화<br>
                FAISS 인덱스로 밀리초 검색
            </div>
        </div>
        <div class="arch-box arch-box-cf">
            <div class="arch-box-title">🔬 트랙 2: 협업 필터링</div>
            <div class="arch-box-desc">
                Book-Crossing 벤치마크 데이터<br>
                Baseline 3 + MF 2 + Neural CF 실험<br>
                방법론 검증 및 인사이트 도출
            </div>
        </div>
    </div>
    <div class="arch-arrow">▼</div>
    <div class="arch-box arch-box-hybrid">
        <div class="arch-box-title">🎨 하이브리드 결합</div>
        <div class="arch-box-desc">
            두 트랙의 강점을 결합해 각 접근의 약점을 상호 보완<br>
            α 파라미터로 개인화 강도 조절 가능
        </div>
    </div>
    <div class="arch-formula">
        최종 점수 = α × 콘텐츠 유사도 + (1 − α) × 인기 신호
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 기술 스택
# =========================
st.markdown("<div class='section-header'>🛠️ 기술 스택</div>", unsafe_allow_html=True)

st.markdown("""
<div>
    <span class="tech-badge">Python 3.12</span>
    <span class="tech-badge">Streamlit</span>
    <span class="tech-badge">SentenceBERT</span>
    <span class="tech-badge">FAISS</span>
    <span class="tech-badge">PyTorch</span>
    <span class="tech-badge">Pandas</span>
    <span class="tech-badge">NumPy</span>
    <span class="tech-badge">Implicit (ALS)</span>
    <span class="tech-badge">알라딘 OpenAPI</span>
    <span class="tech-badge">Book-Crossing Dataset</span>
</div>
""", unsafe_allow_html=True)

# =========================
# 페이지 안내
# =========================
st.markdown("<div class='section-header'>🗺️ 페이지 안내</div>", unsafe_allow_html=True)

page_col1, page_col2 = st.columns(2)

with page_col1:
    st.markdown("""
    <div class="page-card">
        <div class="page-icon">📖</div>
        <div class="page-title">책 추천받기</div>
        <div class="page-desc">
            좋아하는 책 3권을 입력하거나, 취향 태그를 선택하시면<br>
            AI가 유사한 한국 도서를 실시간으로 추천합니다.<br>
            <b>Path A (주관식) / Path B (객관식)</b> 두 가지 진입 경로 지원.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="page-card">
        <div class="page-icon">🧪</div>
        <div class="page-title">시스템 분석 (준비 중)</div>
        <div class="page-desc">
            하이브리드 아키텍처의 상세 설명과 α 파라미터에 따른<br>
            추천 결과 변화를 실험적으로 분석합니다.<br>
            <b>이 프로젝트의 이론적 근거</b>를 다룹니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

with page_col2:
    st.markdown("""
    <div class="page-card">
        <div class="page-icon">📊</div>
        <div class="page-title">협업 필터링 실험</div>
        <div class="page-desc">
            Book-Crossing 데이터로 6종 CF 모델을 벤치마크한 결과.<br>
            Baseline → MF → Neural CF 단계별 성능 비교와<br>
            <b>NCF 실패의 정직한 분석 (Rendle et al. 2020 인용)</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="page-card">
        <div class="page-icon">📝</div>
        <div class="page-title">결론과 한계 (준비 중)</div>
        <div class="page-desc">
            프로젝트 회고, 발견한 인사이트, 그리고 정직한 한계 분석.<br>
            향후 개선 방향과 실서비스 확장 시나리오 제시.<br>
            <b>성숙한 데이터 사이언스 관점</b>을 어필합니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 프로젝트 하이라이트
# =========================
st.markdown("<div class='section-header'>✨ 이 프로젝트의 차별점</div>", unsafe_allow_html=True)

st.markdown("""
<div class="problem-card">
    <div style="color: #D0D0DA; line-height: 1.9; font-size: 14px;">
        일반적인 도서 추천 프로젝트가 <b>영어 벤치마크 데이터셋에 협업 필터링만 돌리는 것</b>과 달리, 
        본 프로젝트는:<br><br>
        <b>1. 실제 한국 도서 API 활용</b> — 알라딘 OpenAPI로 6,974권 실제 데이터 확보<br>
        <b>2. 이중 트랙 설계</b> — 콘텐츠 임베딩(실서비스) + 협업 필터링(방법론 검증)<br>
        <b>3. 데이터 접근성 제약 극복</b> — 국내 유저 이력 없는 현실을 창의적으로 해결<br>
        <b>4. 딥러닝 실패의 정직한 리포트</b> — NCF가 Popularity 수준으로 저조한 실험 결과를 논문 인용과 함께 분석<br>
        <b>5. 실제 서비스 시나리오 반영</b> — 온보딩 UX(주관식/객관식) 설계까지 포함<br>
        <b>6. 실제 한국 도서로 즉시 시연 가능</b> — 배포된 앱에서 실시간 확인
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 하단 정보
# =========================
st.divider()

foot_col1, foot_col2, foot_col3 = st.columns(3)

with foot_col1:
    st.markdown("**📌 프로젝트 정보**")
    st.caption(f"버전: {config['project_meta']['phase']}")
    st.caption(f"기본 α: {config['default_alpha']}")

with foot_col2:
    st.markdown("**📊 데이터 규모**")
    st.caption(f"한국 도서: {config['total_books']:,}권")
    st.caption("Book-Crossing: 115,364 평점")

with foot_col3:
    st.markdown("**⚠️ 유의사항**")
    st.caption("브라우저 자동 번역 기능이 켜져 있으면 UI가 왜곡될 수 있습니다.")
    st.caption("첫 검색 시 AI 모델 로딩으로 30초~1분 소요됩니다.")