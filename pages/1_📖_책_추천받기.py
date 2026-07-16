"""
Page 1 - 책 추천받기 (Path A / Path B)
Streamlit Cloud 최적화: SentenceBERT 지연 로딩
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
import faiss
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="책 추천받기",
    page_icon="📖",
    layout="wide"
)

# 브라우저 자동 번역 방지
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# =========================
# 가벼운 자원만 즉시 로드
# =========================
@st.cache_data
def load_config():
    with open("data/config.json", "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_books():
    return pd.read_parquet("data/books_streamlit.parquet")

@st.cache_data
def load_tags():
    with open("data/tag_templates.json", "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_resource
def load_faiss():
    return faiss.read_index("models/faiss_index.bin")

# 가벼운 것들만 즉시 로드
config = load_config()
df_books = load_books()
tag_templates = load_tags()
faiss_index = load_faiss()

# =========================
# SentenceBERT는 별도 함수로 (지연 로딩)
# =========================
@st.cache_resource
def load_sbert_model():
    """SentenceBERT 지연 로딩 - 실제 검색 시점에 호출"""
    import torch
    from sentence_transformers import SentenceTransformer
    device = "cpu"  # Streamlit Cloud 무료 티어는 GPU 없음
    return SentenceTransformer("jhgan/ko-sroberta-multitask", device=device)

# =========================
# 검색 로직 함수
# =========================
def run_recommendation(query_text_or_texts, alpha, is_tag=False):
    """추천 실행"""
    sbert_model = load_sbert_model()  # 이 시점에 로드

    if is_tag:
        # 태그 → 텍스트 결합
        query_embed = sbert_model.encode(
            [query_text_or_texts],
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype(np.float32)
        user_vector = query_embed
    else:
        # 여러 책 → 평균 벡터
        query_embeds = sbert_model.encode(
            query_text_or_texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        user_vector = query_embeds.mean(axis=0, keepdims=True).astype(np.float32)
        user_vector /= np.linalg.norm(user_vector)

    # FAISS 검색
    top_k = 20
    similarities, indices = faiss_index.search(user_vector, top_k)

    # 결과 조립
    results = df_books.iloc[indices[0]].copy()
    results["content_similarity"] = similarities[0]

    # 정규화 + 하이브리드
    sim_min = results["content_similarity"].min()
    sim_max = results["content_similarity"].max()
    if sim_max > sim_min:
        results["content_normalized"] = (results["content_similarity"] - sim_min) / (sim_max - sim_min)
    else:
        results["content_normalized"] = 1.0

    results["hybrid_score"] = alpha * results["content_normalized"] + (1 - alpha) * results["popularity_score"]
    results = results.sort_values("hybrid_score", ascending=False).head(10).reset_index(drop=True)

    return results

# =========================
# 헤더
# =========================
st.title("📖 책 추천받기")
st.caption("좋아하는 책 3권을 알려주시거나, 취향 태그를 선택하시면 유사한 한국 도서를 추천해드립니다.")

# 첫 사용 안내
if "first_visit" not in st.session_state:
    st.info("💡 **첫 검색 시 AI 모델 로딩으로 1~3분 소요됩니다.** 이후 검색은 즉시 실행됩니다.")
    st.session_state.first_visit = True

st.divider()

# =========================
# 태그 카테고리 그룹핑
# =========================
TAG_CATEGORIES = {
    "📚 장르 (Genre)": ["소설", "에세이", "자기계발", "시", "인문", "과학"],
    "🎨 서브 장르 (Sub-genre)": ["힐링", "판타지", "SF", "추리", "성장", "로맨스"],
    "🎭 분위기 (Mood)": ["따뜻한", "묵직한", "유쾌한", "감동적인", "깊이있는", "긴장감"]
}

# =========================
# 세션 상태 초기화
# =========================
if "path_selected" not in st.session_state:
    st.session_state.path_selected = None
if "results" not in st.session_state:
    st.session_state.results = None
if "used_alpha" not in st.session_state:
    st.session_state.used_alpha = 0.7

# =========================
# 진입 화면 (경로 선택 안 됐을 때)
# =========================
if st.session_state.path_selected is None:
    st.markdown("### 어떻게 추천받으시겠어요?")
    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("### ✍️ Path A: 좋아하는 책이 있어요")
            st.markdown("""
            좋아하는 책 **3권을 텍스트로 입력**하시면,  
            비슷한 스타일·주제의 한국 도서를 추천합니다.

            **적합한 경우:**
            - 취향이 명확한 편이다
            - 최근 감명 깊게 읽은 책이 있다
            - 특정 저자·주제에 관심이 있다
            """)
            if st.button("✍️ Path A로 시작", use_container_width=True, type="primary", key="path_a_btn"):
                st.session_state.path_selected = "A"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("### 🎨 Path B: 태그로 골라볼래요")
            st.markdown("""
            좋아하는 **장르·분위기 태그를 선택**하시면,  
            해당 취향과 매칭되는 한국 도서를 추천합니다.

            **적합한 경우:**
            - 처음 책을 골라보는 초심자
            - 취향이 애매하거나 새로운 발견을 원함
            - 여러 장르를 탐색하고 싶다
            """)
            if st.button("🎨 Path B로 시작", use_container_width=True, key="path_b_btn"):
                st.session_state.path_selected = "B"
                st.rerun()

    # 시스템 설명
    st.divider()
    with st.expander("💡 이 추천 시스템은 어떻게 작동하나요?"):
        st.markdown("""
        - **SentenceBERT**: 한국어 특화 언어 모델로 도서를 벡터로 변환
        - **FAISS**: 6,974권의 한국 도서 임베딩에서 유사도 상위 K개를 밀리초 단위로 검색
        - **하이브리드**: 콘텐츠 유사도 + 인기 신호를 α 파라미터로 결합
        - **최종 점수 = α × 콘텐츠 유사도 + (1-α) × 인기 점수**
        """)

    st.stop()

# =========================
# 경로 변경 옵션
# =========================
c1, c2 = st.columns([5, 1])
with c1:
    if st.session_state.path_selected == "A":
        st.subheader("✍️ Path A: 좋아하는 책 입력")
    else:
        st.subheader("🎨 Path B: 태그 선택")
with c2:
    if st.button("🔄 경로 변경", use_container_width=True):
        st.session_state.path_selected = None
        st.session_state.results = None
        st.rerun()

# =========================
# α 슬라이더 (공통)
# =========================
alpha = st.slider(
    "🎚️ 개인화 강도 (α)",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.1,
    help="1.0 = 순수 콘텐츠 유사도 / 0.0 = 순수 인기순 / 0.7 = 균형(권장)"
)

# α 값 설명
alpha_desc = ""
if alpha >= 0.8:
    alpha_desc = "🎯 **개인화 강조**: 취향과 유사한 도서 우선"
elif alpha >= 0.5:
    alpha_desc = "⚖️ **균형**: 개인화와 인기의 균형 (권장)"
else:
    alpha_desc = "🔥 **인기 강조**: 대중적으로 인기 있는 도서 우선"

st.caption(alpha_desc)

st.divider()

# =========================
# Path A: 주관식 입력
# =========================
if st.session_state.path_selected == "A":
    st.markdown("**좋아하는 책 3권을 입력해주세요.**  \n(제목만이든, 제목+간단한 설명이든 자유롭게)")

    # 예시 제공
    with st.expander("💡 입력 예시 보기"):
        st.code("""
달러구트 꿈 백화점 - 잠들어야 입장 가능한 신비로운 꿈 백화점
불편한 편의점 - 서울역 노숙자와 편의점 이야기
미드나잇 라이브러리 - 인생의 다른 선택들을 담은 무한한 도서관
        """, language=None)

    book_1 = st.text_input("📕 첫 번째 좋아하는 책", placeholder="예: 달러구트 꿈 백화점")
    book_2 = st.text_input("📗 두 번째 좋아하는 책", placeholder="예: 미드나잇 라이브러리")
    book_3 = st.text_input("📘 세 번째 좋아하는 책", placeholder="예: 불편한 편의점")

    queries = [b for b in [book_1, book_2, book_3] if b.strip()]

    if st.button("🔍 추천받기", type="primary", disabled=len(queries) == 0, use_container_width=True):
        # 첫 실행 시 오래 걸릴 수 있음을 명시
        with st.spinner("🤖 AI 모델 로딩 & 유사 도서 검색 중... (첫 실행 시 1~3분)"):
            try:
                results = run_recommendation(queries, alpha, is_tag=False)
                st.session_state.results = results
                st.session_state.used_alpha = alpha
                st.session_state.input_summary = ", ".join(queries)
                st.session_state.path_used = "A"
                st.success("✅ 추천 완료!")
            except Exception as e:
                st.error(f"❌ 검색 중 오류: {str(e)}")

# =========================
# Path B: 태그 선택
# =========================
else:
    st.markdown("**취향에 맞는 태그를 골라주세요.**  \n(카테고리별로 여러 개 선택 가능)")

    selected_tags = []

    for category, tags in TAG_CATEGORIES.items():
        st.markdown(f"**{category}**")
        cols = st.columns(len(tags))
        for i, tag in enumerate(tags):
            with cols[i]:
                if st.checkbox(tag, key=f"tag_{tag}"):
                    selected_tags.append(tag)
        st.write("")

    if selected_tags:
        st.info(f"🏷️ 선택된 태그: {', '.join(selected_tags)}")

    if st.button("🔍 추천받기", type="primary", disabled=len(selected_tags) == 0, use_container_width=True):
        with st.spinner("🤖 AI 모델 로딩 & 태그 매칭 중... (첫 실행 시 1~3분)"):
            try:
                # 태그 → 텍스트 결합
                tag_texts = [tag_templates.get(t, t) for t in selected_tags]
                combined = " . ".join(tag_texts)

                results = run_recommendation(combined, alpha, is_tag=True)
                st.session_state.results = results
                st.session_state.used_alpha = alpha
                st.session_state.input_summary = ", ".join(selected_tags)
                st.session_state.path_used = "B"
                st.success("✅ 추천 완료!")
            except Exception as e:
                st.error(f"❌ 검색 중 오류: {str(e)}")

# =========================
# 결과 표시
# =========================
if st.session_state.results is not None:
    results = st.session_state.results
    used_alpha = st.session_state.used_alpha
    input_summary = st.session_state.input_summary
    path_used = st.session_state.path_used

    st.divider()

    # 결과 헤더
    st.markdown(f"### 🎁 추천 결과 Top 10")
    st.caption(f"경로: **Path {path_used}** | α: **{used_alpha}** | 입력: _{input_summary}_")

    # 뷰 모드 토글
    view_mode = st.radio(
        "표시 방식",
        ["📇 카드 뷰", "📋 테이블 뷰"],
        horizontal=True
    )

    if view_mode == "📇 카드 뷰":
        # 카드 뷰 (2열 그리드)
        for i in range(0, len(results), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                idx = i + j
                if idx >= len(results):
                    break
                book = results.iloc[idx]

                with col:
                    with st.container(border=True):
                        # 표지 이미지 + 정보
                        img_col, info_col = st.columns([1, 3])

                        with img_col:
                            if pd.notna(book.get("cover_url", None)) and book["cover_url"]:
                                st.image(book["cover_url"], use_container_width=True)
                            else:
                                st.markdown("📕")

                        with info_col:
                            st.markdown(f"**#{idx+1} · {book['title']}**")
                            st.caption(f"저자: {book['author_clean']}")
                            st.caption(f"카테고리: {book['cat_main']} > {book['cat_mid']}")

                        # 점수 상세
                        c1, c2, c3 = st.columns(3)
                        c1.metric("유사도", f"{book['content_similarity']:.3f}")
                        c2.metric("인기도", f"{book['popularity_score']:.3f}")
                        c3.metric("최종 점수", f"{book['hybrid_score']:.3f}")

                        # 알라딘 링크
                        if pd.notna(book.get("link", None)) and book["link"]:
                            st.markdown(f"[📚 알라딘에서 자세히 보기]({book['link']})")

    else:
        # 테이블 뷰
        display_df = results[["title", "author_clean", "cat_main", "cat_mid",
                             "content_similarity", "popularity_score", "hybrid_score"]].copy()
        display_df.columns = ["제목", "저자", "대분류", "중분류", "콘텐츠 유사도", "인기 점수", "하이브리드 점수"]
        display_df.index = range(1, len(display_df) + 1)

        styled = (
            display_df.style
            .format({
                "콘텐츠 유사도": "{:.4f}",
                "인기 점수": "{:.4f}",
                "하이브리드 점수": "{:.4f}"
            })
            .background_gradient(subset=["하이브리드 점수"], cmap="Blues")
            .set_properties(**{"text-align": "left", "padding": "8px"})
            .set_table_styles([
                {"selector": "th",
                 "props": [("background-color", "#2E86AB"), ("color", "white"),
                           ("font-weight", "bold"), ("padding", "10px")]}
            ])
        )
        st.dataframe(styled, use_container_width=True)

    st.divider()

    # 추천 시스템 인사이트
    with st.expander("🔍 이 추천은 어떻게 만들어졌나요?"):
        st.markdown(f"""
        **입력 정보 처리:**
        - 입력하신 내용을 한국어 SentenceBERT(`jhgan/ko-sroberta-multitask`)로 벡터화
        - Path A: 3권의 벡터를 평균 내어 취향 벡터 생성
        - Path B: 태그를 자연어로 변환 후 벡터화

        **검색:**
        - FAISS로 6,974권 도서 임베딩에서 유사도 상위 20개 후보 추출
        - 시간 복잡도: O(log N) - 밀리초 단위로 완료

        **하이브리드 결합:**
        - 콘텐츠 유사도 정규화 (0~1 스케일)
        - 알라딘 rating 기반 인기 점수와 결합
        - **최종 점수 = {used_alpha} × 콘텐츠 유사도 + {1-used_alpha:.1f} × 인기 점수**

        **α = {used_alpha}의 의미:**
        - α > 0.5: 개인화 우선 (취향에 가까운 도서 상위)
        - α < 0.5: 인기 우선 (많은 사람이 좋아하는 도서 상위)
        """)

    # 다시 시도 버튼
    if st.button("🔄 다른 조건으로 다시 추천받기", use_container_width=True):
        st.session_state.results = None
        st.rerun()