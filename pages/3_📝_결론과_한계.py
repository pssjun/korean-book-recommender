"""
Page 3 - 결론과 한계
프로젝트 회고 및 향후 개선 방향
"""
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="결론과 한계",
    page_icon="📝",
    layout="wide"
)

# 브라우저 자동 번역 방지
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# =========================
# 커스텀 CSS
# =========================
st.markdown("""
<style>
/* 섹션 헤더 */
.section-header {
    font-size: 26px;
    font-weight: 700;
    margin: 40px 0 20px 0;
    padding-left: 12px;
    border-left: 4px solid #4A9FD1;
}

/* 통계 카드 */
.metric-card {
    background: linear-gradient(145deg, #1E1E2E, #2A2A3E);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.08);
    transition: all 0.3s ease;
    height: 100%;
}
.metric-card:hover {
    transform: translateY(-4px);
    border: 1px solid rgba(74, 159, 209, 0.4);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}
.metric-icon {
    font-size: 36px;
    margin-bottom: 12px;
}
.metric-title {
    font-size: 13px;
    color: #A0A0B0;
    margin-bottom: 8px;
    font-weight: 500;
}
.metric-value {
    font-size: 24px;
    font-weight: 700;
    color: #4A9FD1;
}
.metric-sub {
    font-size: 12px;
    color: #808090;
    margin-top: 4px;
}

/* 인사이트 카드 */
.insight-card {
    background: linear-gradient(145deg, #1E1E2E, #2A2A3E);
    border-radius: 16px;
    padding: 28px;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 16px;
    border-left: 4px solid #4A9FD1;
}
.insight-title {
    font-size: 18px;
    font-weight: 700;
    color: #4A9FD1;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.insight-body {
    color: #D0D0DA;
    line-height: 1.8;
    font-size: 14px;
}
.insight-highlight {
    color: #2ECC71;
    font-weight: 600;
}

/* 한계 카드 */
.limit-card {
    background: linear-gradient(145deg, #2E1E2E, #3A2A3E);
    border-radius: 16px;
    padding: 28px;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 16px;
    border-left: 4px solid #F5B041;
}
.limit-title {
    font-size: 18px;
    font-weight: 700;
    color: #F5B041;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.limit-body {
    color: #D0D0DA;
    line-height: 1.8;
    font-size: 14px;
}

/* 로드맵 카드 */
.roadmap-card {
    background: linear-gradient(145deg, #1E2E1E, #2A3E2A);
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(46, 204, 113, 0.2);
    margin-bottom: 12px;
    border-left: 4px solid #2ECC71;
}
.roadmap-title {
    font-size: 16px;
    font-weight: 700;
    color: #2ECC71;
    margin-bottom: 8px;
}
.roadmap-body {
    color: #D0D0DA;
    font-size: 13px;
    line-height: 1.6;
}

/* Lesson 카드 */
.lesson-card {
    background: linear-gradient(145deg, #1E1E2E, #2A2A3E);
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(255,255,255,0.08);
    height: 100%;
}
.lesson-icon {
    font-size: 32px;
    margin-bottom: 12px;
}
.lesson-title {
    font-size: 16px;
    font-weight: 700;
    color: white;
    margin-bottom: 8px;
}
.lesson-body {
    color: #A0A0B0;
    font-size: 13px;
    line-height: 1.7;
}

/* 하이라이트 박스 */
.highlight-box {
    background: linear-gradient(135deg, rgba(74, 159, 209, 0.1), rgba(46, 204, 113, 0.1));
    border: 1px solid rgba(74, 159, 209, 0.3);
    border-radius: 16px;
    padding: 30px;
    margin: 20px 0;
    text-align: center;
}
.highlight-title {
    font-size: 20px;
    font-weight: 700;
    color: #4A9FD1;
    margin-bottom: 12px;
}
.highlight-body {
    color: #D0D0DA;
    font-size: 14px;
    line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 헤더
# =========================
st.title("📝 결론과 한계")
st.caption("프로젝트의 핵심 성과, 발견한 인사이트, 정직한 한계, 그리고 향후 개선 방향을 정리합니다.")

st.divider()

# =========================
# 핵심 성과
# =========================
st.markdown("<div class='section-header'>🏆 핵심 성과</div>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon">📚</div>
        <div class="metric-title">한국 도서 수집</div>
        <div class="metric-value">6,974권</div>
        <div class="metric-sub">알라딘 API 비동기 병렬</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon">🔬</div>
        <div class="metric-title">CF 벤치마크</div>
        <div class="metric-value">6종 모델</div>
        <div class="metric-sub">Baseline → MF → NCF</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon">📈</div>
        <div class="metric-title">ALS 최고 성능</div>
        <div class="metric-value">+72.4%</div>
        <div class="metric-sub">Baseline 대비 NDCG@10</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon">🚀</div>
        <div class="metric-title">End-to-End</div>
        <div class="metric-value">배포 완료</div>
        <div class="metric-sub">Streamlit Cloud</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 프로젝트 하이라이트
# =========================
st.markdown("""
<div class="highlight-box">
    <div class="highlight-title">🎯 이 프로젝트가 특별한 이유</div>
    <div class="highlight-body">
        일반 도서 추천 프로젝트가 <b>영어 벤치마크 데이터에 CF 하나 돌리기</b>에 그치는 것과 달리,<br>
        본 프로젝트는 <b>실제 문제 정의 → 데이터 접근성 제약 극복 → 이중 트랙 하이브리드 설계 → 정직한 실험 리포트</b>까지<br>
        데이터 사이언스 프로젝트의 <b>전체 흐름을 완결성 있게 수행</b>했습니다.
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 주요 인사이트
# =========================
st.markdown("<div class='section-header'>💡 주요 인사이트</div>", unsafe_allow_html=True)

st.markdown("""
<div class="insight-card">
    <div class="insight-title">
        <span>🎯</span>
        <span>Insight 1: 데이터 접근성 제약을 창의적으로 해결</span>
    </div>
    <div class="insight-body">
        국내 도서 유저-상호작용 데이터가 공개되지 않는 <b>현실적 제약</b>을 인정하고,<br>
        <b>이중 트랙 설계</b>로 해결했습니다:<br><br>
        • <span class="insight-highlight">트랙 1 (실서비스)</span>: 알라딘 API로 수집한 한국 도서에 SentenceBERT 임베딩 + FAISS<br>
        • <span class="insight-highlight">트랙 2 (방법론 검증)</span>: Book-Crossing 벤치마크로 CF 알고리즘 성능 비교<br><br>
        이는 <b>실무에서 자주 마주치는 "데이터가 완벽하지 않은 상황"</b>을 다뤄본 경험이며,<br>
        정직하게 제약을 인정하고 우회하는 접근이 오히려 프로젝트 성숙도를 높였습니다.
    </div>
</div>

<div class="insight-card">
    <div class="insight-title">
        <span>🔬</span>
        <span>Insight 2: 딥러닝이 항상 우수하지 않다 (NCF 실패의 정직한 리포트)</span>
    </div>
    <div class="insight-body">
        Neural Collaborative Filtering은 예상외로 <b>Popularity 수준으로 저조</b>했습니다:<br><br>
        • ALS: NDCG@10 = 0.0444<br>
        • <b>NCF: NDCG@10 = 0.0168 (Popularity와 비슷)</b><br><br>
        원인을 세 가지로 분석했습니다:<br>
        1. Sparsity 99.82%에서 임베딩 학습 신호 부족<br>
        2. 파라미터(51만) > 학습 데이터(20만) → 과적합<br>
        3. <b>Rendle et al. (2020) 논문의 실증적 재현</b>
        (<i>"Neural Collaborative Filtering vs. Matrix Factorization Revisited"</i>)<br><br>
        <span class="insight-highlight">모델 복잡도 ≠ 성능</span>이라는 관점이 확보되었습니다.
    </div>
</div>

<div class="insight-card">
    <div class="insight-title">
        <span>⚖️</span>
        <span>Insight 3: 하이브리드가 CF 단독의 한계를 극복</span>
    </div>
    <div class="insight-body">
        최고 성능 CF 모델(ALS)조차 Precision@10 = 0.017 수준으로 <b>절대값이 낮았습니다</b>.<br>
        이는 협업 필터링 단독으로는 sparse 데이터의 근본적 한계를 극복하기 어려움을 의미합니다.<br><br>
        <b>콘텐츠 기반 접근(알라딘 임베딩)과의 하이브리드</b>로 이를 완화:<br>
        • α 파라미터로 <span class="insight-highlight">개인화 강도 유연 조절</span><br>
        • 콜드 스타트 대응 (신규 유저·신규 도서)<br>
        • 롱테일 도서 노출 가능성 확대<br><br>
        <b>실서비스 시나리오</b>에 실질적으로 적용 가능한 설계입니다.
    </div>
</div>

<div class="insight-card">
    <div class="insight-title">
        <span>🎨</span>
        <span>Insight 4: 온보딩 UX까지 반영한 실서비스적 설계</span>
    </div>
    <div class="insight-body">
        기술적 구현만이 아닌 <b>실제 사용자 경험까지 고려</b>했습니다:<br><br>
        • <b>Path A (주관식)</b>: 좋아하는 책 3권 입력 → 취향 벡터 평균화<br>
        • <b>Path B (객관식)</b>: 태그 조합 → 자연어 변환 후 임베딩<br><br>
        이는 데이터 사이언스가 단순 모델링을 넘어<br>
        <b>서비스 기획·UX 관점</b>까지 확장 가능함을 보여줍니다.
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 한계 (정직한 인정)
# =========================
st.markdown("<div class='section-header'>⚠️ 한계 (정직한 인정)</div>", unsafe_allow_html=True)

st.markdown("""
<div class="limit-card">
    <div class="limit-title">
        <span>📊</span>
        <span>한계 1: 유저 개별 이력이 없어 진정한 개인화가 아님</span>
    </div>
    <div class="limit-body">
        <b>콘텐츠 유사도 + 알라딘 rating(전체 평균 인기)</b>만 사용하므로,<br>
        "유저 A의 과거 이력을 반영한 개인화"는 구현되지 않았습니다.<br><br>
        <b>실서비스에서는</b>:<br>
        • 유저 클릭·구매 이력 축적 후<br>
        • 협업 필터링(ALS)을 하이브리드에 재도입 필요<br>
        • 명시적 피드백 기반 재학습 파이프라인 구축
    </div>
</div>

<div class="limit-card">
    <div class="limit-title">
        <span>🔢</span>
        <span>한계 2: 정량 평가의 근본적 어려움</span>
    </div>
    <div class="limit-body">
        Precision@K, NDCG@K 등 <b>정량 지표는 유저-도서 상호작용 데이터가 필요</b>합니다.<br>
        국내 도서에 대한 이러한 데이터가 부재하여, 하이브리드 최종 시스템에 대한<br>
        <b>정량 평가는 실시할 수 없었습니다</b>.<br><br>
        정성 평가(3가지 시연 시나리오)에 의존한 검증이 이 시스템의 근본적 한계입니다.
    </div>
</div>

<div class="limit-card">
    <div class="limit-title">
        <span>📉</span>
        <span>한계 3: 알라딘 rating의 데이터 편향</span>
    </div>
    <div class="limit-body">
        인기 신호로 사용한 알라딘 rating은 <b>신간 대부분이 0으로 수집</b>되어<br>
        평균값으로 대체되었습니다.<br><br>
        • 신간에 대한 정확한 인기 신호 부재<br>
        • 롱테일 도서 발굴에는 유리하나 실서비스 정확도에는 제약<br>
        • 실제 판매량·조회수 데이터 확보 시 개선 가능
    </div>
</div>

<div class="limit-card">
    <div class="limit-title">
        <span>💾</span>
        <span>한계 4: 배포 환경의 자원 제약</span>
    </div>
    <div class="limit-body">
        Streamlit Cloud 무료 티어의 <b>메모리 1GB 제한</b>으로 인해:<br><br>
        • 원래 계획한 한국어 특화 모델(ko-sroberta, 450MB) 대신<br>
          <b>다국어 경량 모델(MiniLM-L12, 118MB)</b>로 대체<br>
        • 임베딩 차원 축소 (768 → 384)<br>
        • 실서비스에서는 GPU 서버 활용 시 최적 성능 재현 가능
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 향후 개선 방향
# =========================
st.markdown("<div class='section-header'>🚀 향후 개선 방향</div>", unsafe_allow_html=True)

st.markdown("""
<div class="roadmap-card">
    <div class="roadmap-title">🔴 High Priority: 유저 이력 축적 후 CF 재도입</div>
    <div class="roadmap-body">
        실서비스 배포 시 유저 클릭·구매·평점 이력을 축적하고,<br>
        축적된 데이터로 ALS를 재학습하여 하이브리드에 재통합합니다.
    </div>
</div>

<div class="roadmap-card">
    <div class="roadmap-title">🔴 High Priority: A/B 테스트 프레임워크</div>
    <div class="roadmap-body">
        α 파라미터의 최적값을 실증적으로 결정하기 위한 A/B 테스트 파이프라인 구축.<br>
        사용자 클릭률(CTR), 체류 시간, 재방문율 등의 지표로 평가.
    </div>
</div>

<div class="roadmap-card">
    <div class="roadmap-title">🟡 Mid Priority: 다양성 지표 도입</div>
    <div class="roadmap-body">
        Diversity, Serendipity, Coverage 등의 지표를 도입해<br>
        롱테일 도서 노출을 정량적으로 측정하고 최적화합니다.
    </div>
</div>

<div class="roadmap-card">
    <div class="roadmap-title">🟡 Mid Priority: 하이브리드 결합 함수 고도화</div>
    <div class="roadmap-body">
        현재의 선형 결합(α × content + (1-α) × popularity) 대신<br>
        Learning-to-Rank (LTR) 기반 학습 결합으로 확장.
    </div>
</div>

<div class="roadmap-card">
    <div class="roadmap-title">🟢 Low Priority: 정기 재학습 파이프라인</div>
    <div class="roadmap-body">
        신간 유입 시 임베딩 자동 갱신, ALS 정기 재학습 등<br>
        운영 자동화 파이프라인 (Airflow, MLflow 활용).
    </div>
</div>

<div class="roadmap-card">
    <div class="roadmap-title">🟢 Low Priority: 멀티모달 확장</div>
    <div class="roadmap-body">
        도서 표지 이미지도 CLIP 등으로 임베딩하여<br>
        텍스트 + 이미지 멀티모달 유사도 검색으로 확장.
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# Lesson & Learn
# =========================
st.markdown("<div class='section-header'>🎓 Lesson & Learn</div>", unsafe_allow_html=True)

lc1, lc2 = st.columns(2)

with lc1:
    st.markdown("""
    <div class="lesson-card">
        <div class="lesson-icon">💻</div>
        <div class="lesson-title">기술적 배운 점</div>
        <div class="lesson-body">
            • <b>Baseline 없이는 개선 판단 불가능</b> — CF 실험에서 재확인<br><br>
            • <b>Sparse 데이터의 어려움</b> — 99.82% sparsity가 알고리즘 선택에 결정적 영향<br><br>
            • <b>Test set 누수 방지 검증 구조</b> — Optuna 튜닝의 중요성<br><br>
            • <b>비동기(aiohttp)</b> 처리로 대량 API 수집의 실무 감각 확보<br><br>
            • <b>SentenceBERT + FAISS</b> — 벡터 유사도 검색 전체 파이프라인 구축 경험
        </div>
    </div>
    """, unsafe_allow_html=True)

with lc2:
    st.markdown("""
    <div class="lesson-card">
        <div class="lesson-icon">🧠</div>
        <div class="lesson-title">태도적 배운 점</div>
        <div class="lesson-body">
            • <b>정직한 실험 기록의 힘</b> — 실패한 NCF도 프로젝트 가치를 높임<br><br>
            • <b>데이터 제약을 인정하고 우회</b>하는 창의적 접근<br><br>
            • <b>모델 성능이 낮을 때</b> 원인을 데이터·Feature·방법론 차원에서 분리해 해석하는 습관<br><br>
            • <b>완벽한 결과보다 실행 가능한 End-to-End</b>의 가치 재확인<br><br>
            • <b>포트폴리오의 핵심은 절대 성능이 아닌</b> 문제 접근 방법론과 한계 인식
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 마무리
# =========================
st.divider()

st.markdown("""
<div class="highlight-box">
    <div class="highlight-title">📌 프로젝트 마무리</div>
    <div class="highlight-body">
        본 프로젝트는 <b>"국내 서점 추천의 획일화"</b>라는 실제 문제에서 출발하여,<br>
        <b>데이터 수집 → EDA → 이중 트랙 모델링 → 하이브리드 통합 → 배포</b>의<br>
        End-to-End 흐름을 완결성 있게 수행했습니다.<br><br>
        절대 성능 지표만 놓고 보면 만족스럽지 않을 수 있으나,<br>
        <b>그 원인을 데이터·Feature·모델 관점에서 분리 분석</b>하고,<br>
        <b>향후 개선 로드맵</b>을 명확히 정리했다는 점에서 의미 있는 프로젝트라고 생각합니다.<br><br>
        <b>다음 프로젝트</b>에서는 이 한계를 반영하여:<br>
        • LLM 기반 추천 (RAG, GPT-4를 활용한 이유 설명 기능)<br>
        • 이미지 임베딩과의 멀티모달 확장<br>
        • 실서비스 A/B 테스트 프레임워크 구축<br>
        등의 방향으로 확장을 계획하고 있습니다.
    </div>
</div>
""", unsafe_allow_html=True)

st.caption("💡 프로젝트 상세 코드와 실험 노트북은 [GitHub 저장소](https://github.com/pssjun/korean-book-recommender)에서 확인 가능합니다.")