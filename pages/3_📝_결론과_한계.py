"""
Page 3 - 결론과 한계
프로젝트 회고 및 향후 개선 방향 (저널/타임라인 스타일)
"""
import streamlit as st

st.set_page_config(
    page_title="결론과 한계",
    page_icon="📝",
    layout="wide"
)

st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# =========================
# 커스텀 CSS (메인 페이지와 완전히 다른 톤)
# =========================
st.markdown("""
<style>
/* 전체 배경 톤 - 세피아/저널 느낌 */
.journal-header {
    border-bottom: 2px solid #3A3A42;
    padding-bottom: 24px;
    margin-bottom: 32px;
}
.journal-date {
    color: #8A8A95;
    font-size: 13px;
    font-family: 'Courier New', monospace;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.journal-title {
    font-size: 32px;
    font-weight: 800;
    color: #E8E8ED;
}

/* Before/After 스타일 */
.compare-container {
    display: flex;
    gap: 0;
    border-radius: 12px;
    overflow: hidden;
    margin: 24px 0;
    border: 1px solid #3A3A42;
}
.compare-before {
    flex: 1;
    background: #262629;
    padding: 24px;
    border-right: 1px solid #3A3A42;
}
.compare-after {
    flex: 1;
    background: #1A2820;
    padding: 24px;
}
.compare-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.compare-before .compare-label { color: #8A8A95; }
.compare-after .compare-label { color: #5FBF87; }
.compare-value {
    font-size: 24px;
    font-weight: 700;
    color: #E8E8ED;
}

/* 타임라인 스타일 */
.timeline-item {
    position: relative;
    padding-left: 32px;
    padding-bottom: 28px;
    border-left: 2px solid #3A3A42;
    margin-left: 8px;
}
.timeline-item:last-child {
    border-left: 2px solid transparent;
}
.timeline-dot {
    position: absolute;
    left: -7px;
    top: 2px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #4A9FD1;
    border: 2px solid #14141A;
}
.timeline-dot.warn { background: #E0985C; }
.timeline-dot.good { background: #5FBF87; }
.timeline-title {
    font-size: 16px;
    font-weight: 700;
    color: #E8E8ED;
    margin-bottom: 8px;
}
.timeline-body {
    color: #A8A8B5;
    font-size: 14px;
    line-height: 1.75;
}
.timeline-body b {
    color: #C8C8D5;
}
.timeline-body .accent {
    color: #5FBF87;
    font-weight: 600;
}

/* 로드맵 - 심플 리스트 */
.roadmap-row {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    padding: 16px 0;
    border-bottom: 1px solid #2A2A30;
}
.roadmap-row:last-child { border-bottom: none; }
.roadmap-priority {
    flex-shrink: 0;
    width: 60px;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 8px;
    border-radius: 4px;
    text-align: center;
    letter-spacing: 0.5px;
}
.priority-high { background: rgba(224, 152, 92, 0.15); color: #E0985C; }
.priority-mid { background: rgba(90, 150, 220, 0.15); color: #5A96DC; }
.priority-low { background: rgba(140, 140, 150, 0.15); color: #8C8C96; }
.roadmap-content-title {
    font-size: 14px;
    font-weight: 700;
    color: #D8D8E0;
    margin-bottom: 4px;
}
.roadmap-content-desc {
    font-size: 13px;
    color: #8A8A95;
    line-height: 1.6;
}

/* Lesson - 노트카드 스타일 */
.note-card {
    background: #1D1D22;
    border: 1px solid #2E2E36;
    border-radius: 4px;
    padding: 20px;
    position: relative;
    height: 100%;
}
.note-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 3px;
    height: 100%;
    background: #4A9FD1;
    border-radius: 4px 0 0 4px;
}
.note-card.warn::before { background: #E0985C; }
.note-tag {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #6A6A75;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.note-text {
    font-size: 13px;
    color: #B8B8C5;
    line-height: 1.7;
}

/* 인용구 스타일 마무리 */
.closing-quote {
    border-left: 3px solid #4A9FD1;
    padding: 4px 0 4px 24px;
    margin: 32px 0;
    font-size: 15px;
    color: #C8C8D5;
    line-height: 2;
    font-style: italic;
}

/* 섹션 마커 */
.section-marker {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 48px 0 20px 0;
}
.section-marker-num {
    font-family: 'Courier New', monospace;
    font-size: 13px;
    color: #4A9FD1;
    font-weight: 700;
    border: 1px solid #4A9FD1;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.section-marker-title {
    font-size: 20px;
    font-weight: 700;
    color: #E8E8ED;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 저널 헤더
# =========================
st.markdown("""
<div class="journal-header">
    <div class="journal-date">PROJECT RETROSPECTIVE · KOREAN BOOK RECOMMENDER</div>
    <div class="journal-title">📝 결론과 한계</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
이 페이지는 프로젝트를 마무리하며 남기는 회고입니다.  
잘된 점만 나열하지 않고, **무엇을 놓쳤는지, 왜 그런 선택을 했는지, 다음엔 무엇을 할지**를 정리했습니다.
""")

# =========================
# 프로젝트 전/후 비교
# =========================
st.markdown("""
<div class="section-marker">
    <div class="section-marker-num">1</div>
    <div class="section-marker-title">시작과 끝</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="compare-container">
    <div class="compare-before">
        <div class="compare-label">Before — 문제의식</div>
        <div class="compare-value" style="font-size:15px; font-weight:400; line-height:1.7; color:#B8B8C0;">
            국내 서점은 인기순 추천에 의존하고,<br>
            신규 유저 온보딩이 부재하며,<br>
            한국 도서의 상호작용 데이터는<br>
            어디에도 공개되어 있지 않았다.
        </div>
    </div>
    <div class="compare-after">
        <div class="compare-label">After — 결과물</div>
        <div class="compare-value" style="font-size:15px; font-weight:400; line-height:1.7; color:#B8B8C0;">
            알라딘 API로 6,974권을 수집하고,<br>
            콘텐츠 임베딩과 CF 벤치마크를 결합한<br>
            하이브리드 시스템을 설계·배포했다.<br>
            <span style="color:#5FBF87; font-weight:600;">진행 중 실패도 그대로 남겼다.</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 인사이트 - 타임라인
# =========================
st.markdown("""
<div class="section-marker">
    <div class="section-marker-num">2</div>
    <div class="section-marker-title">진행하며 발견한 것들</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="timeline-item">
    <div class="timeline-dot"></div>
    <div class="timeline-title">데이터가 없다는 것 자체가 설계 근거가 되었다</div>
    <div class="timeline-body">
        국내 도서의 유저-상호작용 데이터는 어디에도 공개되어 있지 않다.<br>
        이 제약을 우회하는 대신 <b>정면으로 설계에 반영</b>했다.<br>
        트랙 1(알라딘 콘텐츠 임베딩)은 실서비스를, 트랙 2(Book-Crossing)는 방법론 검증을 각각 담당하도록 분리했다.<br>
        제약을 숨기지 않고 구조에 드러낸 것이 결과적으로 더 정직한 설계가 됐다.
    </div>
</div>

<div class="timeline-item">
    <div class="timeline-dot warn"></div>
    <div class="timeline-title">NCF는 기대만큼 작동하지 않았다</div>
    <div class="timeline-body">
        ALS의 NDCG@10이 0.0444였던 반면, Neural CF는 <b>0.0168</b> — Popularity 수준까지 떨어졌다.<br>
        원인은 sparsity 99.82%에서의 임베딩 학습 부족, 그리고 파라미터(51만) 대비 부족한 학습 데이터(20만).<br>
        Rendle et al.(2020)의 지적, <span class="accent">"잘 튜닝된 MF가 NCF보다 나을 수 있다"</span>가 이 프로젝트에서도 그대로 재현됐다.<br>
        결과를 숨기지 않고 원인을 추적하는 편이 더 남는 게 많았다.
    </div>
</div>

<div class="timeline-item">
    <div class="timeline-dot"></div>
    <div class="timeline-title">가장 좋은 모델도 절대적으로는 약했다</div>
    <div class="timeline-body">
        최고 성능인 ALS조차 Precision@10 = 0.017. 협업 필터링만으로는 부족했다.<br>
        그래서 콘텐츠 기반 접근을 <b>보조가 아니라 주력</b>으로 세우고,<br>
        α 파라미터로 두 신호의 비중을 유저가 직접 조절할 수 있게 열어뒀다.
    </div>
</div>

<div class="timeline-item">
    <div class="timeline-dot good"></div>
    <div class="timeline-title">모델링보다 UX 설계에 시간이 더 들었다</div>
    <div class="timeline-body">
        Path A(책 3권 입력)와 Path B(태그 선택)를 나눈 이유는 단순하다 —<br>
        <b>취향이 명확한 사람과 그렇지 않은 사람은 다른 방식으로 도와야 한다.</b><br>
        기술적으로는 같은 임베딩 파이프라인을 타지만, 진입 경험은 완전히 다르게 설계했다.
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 한계 - 탭으로 구성
# =========================
st.markdown("""
<div class="section-marker">
    <div class="section-marker-num">3</div>
    <div class="section-marker-title">한계 — 그대로 인정하는 부분</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "개인화의 한계",
    "평가의 한계",
    "데이터 편향",
    "배포 환경 제약"
])

with tab1:
    st.markdown("""
    <div class="note-card">
        <div class="note-tag">Limitation · Personalization</div>
        <div class="note-text">
            현재 하이브리드는 <b>콘텐츠 유사도 + 전체 평균 인기 신호</b>만 결합한다.<br>
            "유저 A의 과거 이력"은 반영되지 않는다 — 애초에 그런 데이터가 없기 때문이다.<br><br>
            실서비스라면 클릭·구매·평점 로그를 쌓고, 그 데이터로 ALS를 다시 학습시켜
            하이브리드에 재통합하는 단계가 필요하다. 지금은 <b>"콜드 스타트를 해결한 시스템"</b>이지,
            <b>"개인화를 완성한 시스템"</b>은 아니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class="note-card warn">
        <div class="note-tag">Limitation · Evaluation</div>
        <div class="note-text">
            Precision@K, NDCG@K 같은 정량 지표는 유저-도서 상호작용 데이터가 있어야 계산할 수 있다.<br>
            국내 도서에는 이 데이터가 없어서, <b>최종 하이브리드 시스템은 정량 평가를 못 했다.</b><br><br>
            대신 세 가지 시나리오로 정성 평가를 했는데, 이건 "그럴듯해 보인다"는 확인이지
            "실제로 더 낫다"는 증명이 아니다. 이 페이지에서 가장 솔직하게 인정해야 할 지점이다.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown("""
    <div class="note-card warn">
        <div class="note-tag">Limitation · Data Bias</div>
        <div class="note-text">
            알라딘 rating을 인기 신호로 썼는데, <b>신간 대부분은 rating이 0</b>이라 평균값으로 채워 넣었다.<br>
            이건 "신간이 저평가되지 않도록"이라는 의도였지만, 동시에 <b>진짜 인기 신호를 흐릿하게</b> 만드는
            선택이기도 하다. 실제 판매량이나 조회수 데이터가 있었다면 훨씬 정확했을 것이다.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab4:
    st.markdown("""
    <div class="note-card warn">
        <div class="note-tag">Limitation · Infra</div>
        <div class="note-text">
            Streamlit Cloud 무료 티어의 메모리 1GB 제한 때문에, 원래 쓰려던 한국어 특화 모델
            (ko-sroberta, 450MB) 대신 <b>다국어 경량 모델(MiniLM, 118MB)</b>로 바꿨다.<br>
            임베딩 차원도 768 → 384로 줄었다. 성능 손실이 어느 정도인지는 정량적으로 확인하지 못했다 —
            이것도 정직하게 남겨야 할 부분이다.
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 향후 개선 방향
# =========================
st.markdown("""
<div class="section-marker">
    <div class="section-marker-num">4</div>
    <div class="section-marker-title">다음에 한다면</div>
</div>
""", unsafe_allow_html=True)

roadmap_items = [
    ("HIGH", "priority-high", "유저 이력 기반 CF 재도입", "실서비스 배포 후 클릭·구매·평점 데이터를 축적하고, 그 데이터로 ALS를 재학습해 하이브리드에 다시 통합한다."),
    ("HIGH", "priority-high", "A/B 테스트로 α값 실증", "지금 α=0.7은 직관적 선택이다. 실제 CTR, 체류시간, 재방문율로 최적값을 검증하는 절차가 필요하다."),
    ("MID", "priority-mid", "다양성 지표 도입", "Diversity, Serendipity, Coverage를 도입해 롱테일 노출을 숫자로 측정하고 관리한다."),
    ("MID", "priority-mid", "결합 함수 고도화", "지금의 선형 결합(α × content + (1-α) × popularity)을 Learning-to-Rank 기반으로 확장한다."),
    ("LOW", "priority-low", "정기 재학습 파이프라인", "신간 임베딩 자동 갱신, ALS 정기 재학습 등 운영 자동화를 구축한다."),
    ("LOW", "priority-low", "멀티모달 확장", "표지 이미지를 CLIP 등으로 임베딩해 텍스트 + 이미지 유사도로 확장한다."),
]

for priority, css_class, title, desc in roadmap_items:
    st.markdown(f"""
    <div class="roadmap-row">
        <div class="roadmap-priority {css_class}">{priority}</div>
        <div>
            <div class="roadmap-content-title">{title}</div>
            <div class="roadmap-content-desc">{desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# Lesson & Learn - 노트카드
# =========================
st.markdown("""
<div class="section-marker">
    <div class="section-marker-num">5</div>
    <div class="section-marker-title">남은 것</div>
</div>
""", unsafe_allow_html=True)

lc1, lc2 = st.columns(2)

with lc1:
    st.markdown("""
    <div class="note-card">
        <div class="note-tag">기술적으로 남은 것</div>
        <div class="note-text">
            Baseline 없이는 "개선"이라는 말 자체가 성립하지 않는다는 걸 CF 실험에서 다시 확인했다.<br><br>
            Sparsity 99.82%라는 숫자 하나가 알고리즘 선택 전체를 좌우한다는 것도 몸으로 배웠다.<br><br>
            SentenceBERT + FAISS로 검색 파이프라인을 처음부터 끝까지 직접 붙여본 경험은
            다음 프로젝트에 그대로 재사용할 수 있는 자산이 됐다.
        </div>
    </div>
    """, unsafe_allow_html=True)

with lc2:
    st.markdown("""
    <div class="note-card">
        <div class="note-tag">태도로 남은 것</div>
        <div class="note-text">
            NCF가 실패했을 때 그 결과를 지우고 싶은 유혹이 있었다.<br>
            대신 원인을 추적해서 남기는 쪽을 택했고, 결과적으로 이게 더 남는 기록이 됐다.<br><br>
            포트폴리오의 값어치는 <b>지표가 얼마나 높은가</b>가 아니라
            <b>왜 그 숫자가 나왔는지 설명할 수 있는가</b>에 있다는 걸 이번에 배웠다.
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 마무리
# =========================
st.markdown("""
<div class="closing-quote">
"이 프로젝트는 완성된 추천 시스템이라기보다, <br>
데이터가 부족한 상황에서 무엇을 우선순위에 둘지 판단해 나간 기록에 가깝다.<br>
다음 프로젝트에서는 이번에 남긴 한계들을 출발점으로 삼으려 한다."
</div>
""", unsafe_allow_html=True)

st.divider()
st.caption("📎 프로젝트 코드와 실험 노트북: [GitHub 저장소](https://github.com/pssjun/korean-book-recommender)")