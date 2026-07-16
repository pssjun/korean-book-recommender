"""
Page 2 - 협업 필터링 실험 결과
Book-Crossing 데이터셋 기반 6종 CF 모델 성능 비교
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="협업 필터링 실험",
    page_icon="📊",
    layout="wide"
)

# 브라우저 자동 번역 방지
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# =========================
# 데이터 로드
# =========================
@st.cache_data
def load_cf_results():
    """CF 실험 결과 로드"""
    csv_path = Path("data/cf_final_comparison.csv")
    
    if csv_path.exists():
        return pd.read_csv(csv_path, index_col=0)
    
    # 파일 없으면 하드코딩 데이터 (fallback)
    data = {
        "Category": ["Baseline", "Baseline", "Baseline", "MF", "MF", "Neural"],
        "precision@5": [0.0084, 0.0026, 0.0129, 0.0207, 0.0231, 0.0076],
        "precision@10": [0.0068, 0.0022, 0.0090, 0.0148, 0.0172, 0.0069],
        "precision@20": [0.0055, 0.0022, 0.0059, 0.0108, 0.0131, 0.0057],
        "recall@5": [0.0155, 0.0040, 0.0251, 0.0363, 0.0425, 0.0135],
        "recall@10": [0.0260, 0.0061, 0.0335, 0.0515, 0.0605, 0.0258],
        "recall@20": [0.0430, 0.0125, 0.0420, 0.0722, 0.0879, 0.0427],
        "ndcg@5": [0.0138, 0.0040, 0.0231, 0.0344, 0.0389, 0.0125],
        "ndcg@10": [0.0172, 0.0046, 0.0258, 0.0388, 0.0444, 0.0168],
        "ndcg@20": [0.0223, 0.0066, 0.0284, 0.0453, 0.0530, 0.0220],
        "mrr": [0.0264, 0.0089, 0.0368, 0.0589, 0.0645, 0.0259]
    }
    df = pd.DataFrame(data, index=["Popularity", "User-CF", "Item-CF", "SVD", "ALS", "NCF"])
    return df

cf_results = load_cf_results()

# =========================
# 헤더
# =========================
st.title("📊 협업 필터링 실험 결과")
st.markdown("Book-Crossing 벤치마크 데이터로 CF 알고리즘 6종을 실험적으로 비교 분석했습니다.")
st.divider()

# =========================
# 최고 성능 모델 요약 카드
# =========================
best_model = cf_results["ndcg@10"].idxmax()
baseline_best_ndcg = cf_results.loc[["Popularity", "User-CF", "Item-CF"], "ndcg@10"].max()
improvement_pct = (cf_results.loc[best_model, "ndcg@10"] - baseline_best_ndcg) / baseline_best_ndcg * 100

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("최고 모델", best_model, help="NDCG@10 기준")
with col2:
    st.metric(
        "NDCG@10", 
        f"{cf_results.loc[best_model, 'ndcg@10']:.4f}",
        f"+{improvement_pct:.1f}% vs Baseline"
    )
with col3:
    st.metric(
        "Precision@10",
        f"{cf_results.loc[best_model, 'precision@10']:.4f}"
    )
with col4:
    st.metric(
        "실험 모델 수",
        f"{len(cf_results)}종",
        help="Baseline 3 + MF 2 + Neural 1"
    )

st.divider()

# =========================
# 실험 설계 요약
# =========================
st.header("🧪 실험 설계")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("""
    #### 데이터셋
    - **Book-Crossing** (Kaggle 벤치마크)
    - 원본: 27만 유저 × 27만 도서 × 100만 평점
    - 전처리 후: **6,862 유저 × 9,096 도서 × 115,364 평점**
    - **Sparsity: 99.82%**
    """)

with col_b:
    st.markdown("""
    #### 평가 지표
    - **Precision@K**: Top K 중 실제 관심 비율
    - **Recall@K**: 실제 관심 중 Top K 포함 비율
    - **NDCG@K**: 순위 반영 정확도
    - **MRR**: 첫 관련 아이템의 역순위
    """)

st.divider()

# =========================
# 모델별 성능 비교 - 인터랙티브 시각화
# =========================
st.header("📈 모델별 성능 비교")

# 지표 선택
selected_metric = st.radio(
    "비교할 지표 선택",
    ["ndcg@10", "precision@10", "recall@10", "mrr"],
    horizontal=True,
    format_func=lambda x: {
        "ndcg@10": "NDCG@10 (순위 반영)",
        "precision@10": "Precision@10 (정확도)",
        "recall@10": "Recall@10 (커버리지)",
        "mrr": "MRR (첫 정답 위치)"
    }[x]
)

# 정렬된 데이터
sorted_data = cf_results.sort_values(selected_metric, ascending=True)

# 카테고리별 색상
color_map = {
    "Baseline": "#95A5A6",
    "MF": "#2ECC71",
    "Neural": "#E74C3C"
}
bar_colors = [color_map[cat] for cat in sorted_data["Category"]]

# Plotly 막대 그래프
fig = go.Figure()
fig.add_trace(go.Bar(
    y=sorted_data.index,
    x=sorted_data[selected_metric],
    orientation='h',
    marker_color=bar_colors,
    text=[f"{v:.4f}" for v in sorted_data[selected_metric]],
    textposition="outside"
))

fig.update_layout(
    title=f"{selected_metric.upper()} 성능 순위",
    xaxis_title=selected_metric,
    yaxis_title="",
    height=400,
    margin=dict(l=100),
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# 카테고리 범례
col_l1, col_l2, col_l3 = st.columns(3)
col_l1.markdown(f"<div style='background:{color_map['Baseline']};color:white;padding:8px;text-align:center;border-radius:4px;'>Baseline (Popularity, User-CF, Item-CF)</div>", unsafe_allow_html=True)
col_l2.markdown(f"<div style='background:{color_map['MF']};color:white;padding:8px;text-align:center;border-radius:4px;'>Matrix Factorization (SVD, ALS)</div>", unsafe_allow_html=True)
col_l3.markdown(f"<div style='background:{color_map['Neural']};color:white;padding:8px;text-align:center;border-radius:4px;'>Neural CF</div>", unsafe_allow_html=True)

st.divider()

# =========================
# 전체 지표 비교표
# =========================
st.header("📋 전체 성능 비교표")

display_df = cf_results.copy()

# 스타일링
styled = (
    display_df.style
    .format({col: "{:.4f}" for col in display_df.columns if col != "Category"})
    .background_gradient(subset=["ndcg@10"], cmap="Greens")
    .background_gradient(subset=["precision@10"], cmap="Blues")
    .background_gradient(subset=["recall@10"], cmap="Purples")
    .set_properties(**{"text-align": "center", "padding": "8px"})
    .set_table_styles([
        {"selector": "th",
         "props": [("background-color", "#2E86AB"), ("color", "white"),
                   ("font-weight", "bold"), ("padding", "10px"),
                   ("text-align", "center")]}
    ])
)

st.dataframe(styled, use_container_width=True)

st.caption("📌 초록 그라데이션: NDCG@10 | 파랑: Precision@10 | 보라: Recall@10")

st.divider()

# =========================
# Baseline 대비 개선폭 시각화
# =========================
st.header("📊 Baseline 대비 개선폭")

baseline_best_row = cf_results.loc[["Popularity", "User-CF", "Item-CF"], "ndcg@10"].idxmax()
baseline_best_val = cf_results.loc[baseline_best_row, "ndcg@10"]

improvements = {}
for model in ["SVD", "ALS", "NCF"]:
    imp = (cf_results.loc[model, "ndcg@10"] - baseline_best_val) / baseline_best_val * 100
    improvements[model] = imp

imp_df = pd.DataFrame({
    "Model": list(improvements.keys()),
    "Improvement (%)": list(improvements.values())
})

fig_imp = go.Figure()

imp_colors = ["green" if v > 0 else "red" for v in improvements.values()]

fig_imp.add_trace(go.Bar(
    x=imp_df["Model"],
    y=imp_df["Improvement (%)"],
    marker_color=imp_colors,
    text=[f"{v:+.1f}%" for v in improvements.values()],
    textposition="outside"
))

fig_imp.add_hline(y=0, line_dash="dash", line_color="gray")
fig_imp.update_layout(
    title=f"vs {baseline_best_row} (Baseline 최고)",
    yaxis_title="NDCG@10 개선폭 (%)",
    height=400,
    showlegend=False
)

st.plotly_chart(fig_imp, use_container_width=True)

st.divider()

# =========================
# 핵심 인사이트
# =========================
st.header("💡 핵심 인사이트")

with st.container(border=True):
    st.markdown(f"""
    #### 1. ALS가 최고 성능 (예상대로)
    - **NDCG@10 개선폭: +{improvement_pct:.1f}%** (Baseline 최고 대비)
    - Precision@10 개선폭: +91.1%
    - BM25 weighting + 잠재 요인 학습이 sparse 데이터에 이상적으로 적합함을 실증
    """)

with st.container(border=True):
    ncf_gap = (cf_results.loc["ALS", "ndcg@10"] - cf_results.loc["NCF", "ndcg@10"]) / cf_results.loc["ALS", "ndcg@10"] * 100
    
    st.markdown(f"""
    #### 2. NCF가 실패한 예상외 발견 ⚠️
    - **NCF < Popularity < Item-CF < SVD < ALS**
    - NCF의 NDCG@10은 ALS 대비 **-{ncf_gap:.1f}%**
    - Popularity 수준으로 저조 (신경망의 표현력 무용지물)
    
    **원인 분석:**
    - 극심한 sparsity(99.82%)에서 임베딩 학습 신호 부족
    - 파라미터(51만) > 학습 데이터(20만) → 과적합 위험
    - **Rendle et al. (2020) 논문의 실증적 재현**  
      *"Neural Collaborative Filtering vs. Matrix Factorization Revisited"*
    """)

with st.container(border=True):
    st.markdown("""
    #### 3. User-CF의 근본적 한계
    - NDCG@10: 0.0046 (전체 최하위)
    - Sparsity 99.82%에서 유저 간 유사도 계산 자체가 신뢰 불가
    - 두 유저 간 공통 평가 도서가 거의 없어 코사인 유사도가 노이즈로 작용
    """)

with st.container(border=True):
    st.markdown("""
    #### 4. 절대값이 낮은 이유 (정직한 리포트)
    - 최고 성능 ALS조차 Precision@10 = 0.017
    - 9,096권 중 유저 한 명이 진짜 좋아할 소수를 정확히 맞추는 것은 근본적으로 어려운 문제
    - Book-Crossing 논문 및 타 벤치마크에서도 유사한 수치 관찰됨
    - **협업 필터링 단독의 한계 → 하이브리드의 필요성 정량적 근거**
    """)

st.divider()

# =========================
# 프로젝트 스토리에 미치는 영향
# =========================
st.header("🔗 하이브리드 시스템으로의 연결")

st.markdown("""
협업 필터링 실험은 다음 세 가지 근거를 확보했습니다:

**1️⃣ 방법론 검증**  
Book-Crossing 벤치마크로 CF 알고리즘의 상대 우열을 실증 (ALS > SVD > Item-CF > Popularity > NCF > User-CF)

**2️⃣ 딥러닝의 한계 인식**  
NCF 실패로 "모델 복잡도 ≠ 성능"이라는 성숙한 관점 확보

**3️⃣ 콘텐츠 접근의 필요성**  
CF 단독으로 낮은 절대 성능 → 콘텐츠 기반 접근(알라딘 임베딩)과의 하이브리드가 필수임을 실증

이러한 발견들이 **`책 추천받기` 페이지의 하이브리드 시스템 설계 근거**가 됩니다.
""")

# 하단
st.divider()
st.caption("💡 실험 상세 코드는 GitHub 저장소의 notebook에서 확인 가능합니다.")