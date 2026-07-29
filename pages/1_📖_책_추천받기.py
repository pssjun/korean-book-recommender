"""
Page 1 - 책 추천받기 (Path A / Path B)
FastAPI 백엔드를 호출하는 프론트엔드 전용 구현
"""
import os
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="책 추천받기", page_icon="📖", layout="wide")
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# =========================
# API 설정
# =========================
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def call_api(endpoint: str, payload: dict, timeout: int = 60):
    """추천 API 호출"""
    try:
        res = requests.post(f"{API_BASE_URL}{endpoint}", json=payload, timeout=timeout)
        res.raise_for_status()
        return res.json(), None
    except requests.exceptions.ConnectionError:
        return None, "API 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요."
    except requests.exceptions.Timeout:
        return None, "요청 시간이 초과되었습니다."
    except requests.exceptions.HTTPError as e:
        detail = ""
        try:
            detail = res.json().get("detail", "")
        except Exception:
            pass
        return None, f"API 오류 ({res.status_code}): {detail or e}"
    except Exception as e:
        return None, f"알 수 없는 오류: {e}"


@st.cache_data(ttl=60)
def check_api_health():
    """API 헬스체크"""
    try:
        res = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return res.json() if res.ok else None
    except Exception:
        return None


@st.cache_data(ttl=300)
def fetch_tags():
    """사용 가능한 태그 목록 조회"""
    try:
        res = requests.get(f"{API_BASE_URL}/tags", timeout=5)
        return res.json().get("tags", []) if res.ok else []
    except Exception:
        return []


# =========================
# 헤더 + API 상태
# =========================
st.title("📖 책 추천받기")
st.caption("좋아하는 책 3권을 알려주시거나, 취향 태그를 선택하시면 유사한 한국 도서를 추천해드립니다.")

health = check_api_health()
if health and health.get("model_loaded"):
    st.success(
        f"✅ 추천 API 연결됨 · 도서 {health.get('total_books', 0):,}권 · "
        f"인덱스 {health.get('index_size', 0):,}개"
    )
else:
    st.error(
        f"❌ 추천 API에 연결할 수 없습니다 ({API_BASE_URL})\n\n"
        "터미널에서 다음 명령으로 API 서버를 실행해주세요:\n\n"
        "`docker run -p 8000:8000 book-recommender-api`"
    )
    st.stop()

st.divider()

# =========================
# 태그 카테고리
# =========================
TAG_CATEGORIES = {
    "📚 장르 (Genre)": ["소설", "에세이", "자기계발", "시", "인문", "과학"],
    "🎨 서브 장르 (Sub-genre)": ["힐링", "판타지", "SF", "추리", "성장", "로맨스"],
    "🎭 분위기 (Mood)": ["따뜻한", "묵직한", "유쾌한", "감동적인", "깊이있는", "긴장감"],
}

# =========================
# 세션 상태
# =========================
if "path_selected" not in st.session_state:
    st.session_state.path_selected = None
if "api_response" not in st.session_state:
    st.session_state.api_response = None

# =========================
# 진입 화면
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
            """)
            if st.button("✍️ Path A로 시작", use_container_width=True, type="primary"):
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
            - 새로운 발견을 원함
            """)
            if st.button("🎨 Path B로 시작", use_container_width=True):
                st.session_state.path_selected = "B"
                st.rerun()

    st.divider()
    with st.expander("🏗️ 시스템 아키텍처"):
        st.markdown(f"""
        이 서비스는 **프론트엔드와 추천 엔진이 분리된 구조**로 동작합니다.Streamlit (Frontend)
          │  HTTP POST
          ▼
    FastAPI (Docker Container)
          ├─ SentenceBERT 임베딩
          ├─ FAISS 유사도 검색
          └─ 하이브리드 스코어 결합- **API Base URL**: `{API_BASE_URL}`
        - 모델은 API 서버 기동 시 1회만 로딩되어 메모리에 상주합니다
        - 요청별 처리 시간은 응답의 `elapsed_ms` 필드로 확인 가능합니다
        """)

    st.stop()

# =========================
# 경로 변경 + α 슬라이더
# =========================
c1, c2 = st.columns([5, 1])
with c1:
    st.subheader("✍️ Path A: 좋아하는 책 입력" if st.session_state.path_selected == "A" else "🎨 Path B: 태그 선택")
with c2:
    if st.button("🔄 경로 변경", use_container_width=True):
        st.session_state.path_selected = None
        st.session_state.api_response = None
        st.rerun()

alpha = st.slider(
    "🎚️ 개인화 강도 (α)", min_value=0.0, max_value=1.0, value=0.7, step=0.1,
    help="1.0 = 순수 콘텐츠 유사도 / 0.0 = 순수 인기순 / 0.7 = 균형(권장)"
)

if alpha >= 0.8:
    st.caption("🎯 **개인화 강조**: 취향과 유사한 도서 우선")
elif alpha >= 0.5:
    st.caption("⚖️ **균형**: 개인화와 인기의 균형 (권장)")
else:
    st.caption("🔥 **인기 강조**: 대중적으로 인기 있는 도서 우선")

st.divider()

# =========================
# Path A
# =========================
if st.session_state.path_selected == "A":
    st.markdown("**좋아하는 책 3권을 입력해주세요.**")

    with st.expander("💡 입력 예시 보기"):
        st.code("""달러구트 꿈 백화점
미드나잇 라이브러리
불편한 편의점""", language=None)

    book_1 = st.text_input("📕 첫 번째", placeholder="예: 달러구트 꿈 백화점")
    book_2 = st.text_input("📗 두 번째", placeholder="예: 미드나잇 라이브러리")
    book_3 = st.text_input("📘 세 번째", placeholder="예: 불편한 편의점")

    queries = [b for b in [book_1, book_2, book_3] if b.strip()]

    if st.button("🔍 추천받기", type="primary", disabled=len(queries) == 0, use_container_width=True):
        with st.spinner("🤖 추천 API 호출 중..."):
            data, err = call_api(
                "/recommend/path-a",
                {"books": queries, "top_k": 10, "alpha": alpha},
            )
        if err:
            st.error(err)
        else:
            st.session_state.api_response = data
            st.success(f"✅ 추천 완료! (처리 시간: {data['elapsed_ms']}ms)")

# =========================
# Path B
# =========================
else:
    st.markdown("**취향에 맞는 태그를 골라주세요.**")

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
        with st.spinner("🤖 추천 API 호출 중..."):
            data, err = call_api(
                "/recommend/path-b",
                {"tags": selected_tags, "top_k": 10, "alpha": alpha},
            )
        if err:
            st.error(err)
        else:
            st.session_state.api_response = data
            st.success(f"✅ 추천 완료! (처리 시간: {data['elapsed_ms']}ms)")

# =========================
# 결과 표시
# =========================
if st.session_state.api_response:
    data = st.session_state.api_response
    results = data["results"]

    st.divider()
    st.markdown("### 🎁 추천 결과 Top 10")
    st.caption(
        f"경로: **Path {data['path']}** | α: **{data['alpha']}** | "
        f"입력: _{data['query_summary']}_ | "
        f"검색 대상: {data['total_books_searched']:,}권 | "
        f"처리 시간: {data['elapsed_ms']}ms"
    )

    view_mode = st.radio("표시 방식", ["📇 카드 뷰", "📋 테이블 뷰"], horizontal=True)

    if view_mode == "📇 카드 뷰":
        for i in range(0, len(results), 2):
            cols = st.columns(2, gap="medium")
            for j, col in enumerate(cols):
                idx = i + j
                if idx >= len(results):
                    break
                book = results[idx]
                with col:
                    with st.container(border=True):
                        img_col, info_col = st.columns([1, 3])
                        with img_col:
                            if book.get("cover_url"):
                                st.image(book["cover_url"], use_container_width=True)
                            else:
                                st.markdown("📕")
                        with info_col:
                            st.markdown(f"**#{book['rank']} · {book['title']}**")
                            st.caption(f"저자: {book['author']}")
                            st.caption(f"{book['category_main']} > {book['category_mid']}")

                        m1, m2, m3 = st.columns(3)
                        m1.metric("유사도", f"{book['content_similarity']:.3f}")
                        m2.metric("인기도", f"{book['popularity_score']:.3f}")
                        m3.metric("최종", f"{book['hybrid_score']:.3f}")

                        if book.get("link"):
                            st.markdown(f"[📚 알라딘에서 보기]({book['link']})")
    else:
        df = pd.DataFrame(results)[
            ["rank", "title", "author", "category_main", "category_mid",
             "content_similarity", "popularity_score", "hybrid_score"]
        ]
        df.columns = ["순위", "제목", "저자", "대분류", "중분류", "콘텐츠 유사도", "인기 점수", "하이브리드 점수"]
        st.dataframe(
            df.style.format({
                "콘텐츠 유사도": "{:.4f}",
                "인기 점수": "{:.4f}",
                "하이브리드 점수": "{:.4f}",
            }).background_gradient(subset=["하이브리드 점수"], cmap="Blues"),
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
    with st.expander("🔍 이 추천은 어떻게 만들어졌나요?"):
        st.markdown(f"""
        **처리 흐름**
        1. Streamlit이 사용자 입력을 받아 FastAPI에 HTTP POST 요청
        2. API 서버가 입력을 SentenceBERT로 벡터화
        3. FAISS로 {data['total_books_searched']:,}권 중 유사 도서 검색
        4. 콘텐츠 유사도와 인기 신호를 α로 결합해 최종 순위 산출

        **최종 점수** = {data['alpha']} × 콘텐츠 유사도 + {1 - data['alpha']:.1f} × 인기 점수

        **이번 요청 처리 시간**: {data['elapsed_ms']}ms
        """)

    if st.button("🔄 다른 조건으로 다시 추천받기", use_container_width=True):
        st.session_state.api_response = None
        st.rerun()