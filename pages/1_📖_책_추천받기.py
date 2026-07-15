# =========================
# 한국 도서 추천 페이지
# pages/1_📖_책_추천받기.py
# =========================

from pathlib import Path

import faiss
import numpy as np
import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer


# =========================
# 페이지 설정
# =========================
st.set_page_config(
    page_title="책 추천받기",
    page_icon="📖",
    layout="wide",
)


# =========================
# 경로 및 모델 설정
# =========================
BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = BASE_DIR / "data" / "books_streamlit.parquet"
INDEX_PATH = BASE_DIR / "models" / "faiss_index.bin"

MODEL_ID = "jhgan/ko-sroberta-multitask"


# =========================
# 데이터 로드
# =========================
@st.cache_data(show_spinner=False)
def load_books(data_path: Path) -> pd.DataFrame:
    """Streamlit 추천용 도서 데이터를 불러온다."""

    if not data_path.exists():
        raise FileNotFoundError(
            "도서 데이터 파일을 찾을 수 없습니다.\n\n"
            f"확인 경로: {data_path}"
        )

    books = pd.read_parquet(data_path)

    if books.empty:
        raise ValueError("도서 데이터가 비어 있습니다.")

    required_columns = {"title"}

    missing_columns = required_columns - set(books.columns)

    if missing_columns:
        raise ValueError(
            "도서 데이터에 필수 컬럼이 없습니다.\n\n"
            f"누락 컬럼: {sorted(missing_columns)}"
        )

    return books.reset_index(drop=True)


# =========================
# FAISS 인덱스 로드
# =========================
@st.cache_resource(show_spinner=False)
def load_faiss_index(index_path: Path):
    """
    FAISS 인덱스를 메모리에서 역직렬화한다.

    Windows 한글 경로에서 faiss.read_index()가
    Illegal byte sequence 오류를 발생시키는 문제를 회피한다.
    """

    if not index_path.exists():
        raise FileNotFoundError(
            "FAISS 인덱스 파일을 찾을 수 없습니다.\n\n"
            f"확인 경로: {index_path}"
        )

    if index_path.stat().st_size == 0:
        raise ValueError("FAISS 인덱스 파일 크기가 0바이트입니다.")

    with open(index_path, "rb") as file:
        index_bytes = file.read()

    index_array = np.frombuffer(index_bytes, dtype=np.uint8).copy()

    try:
        loaded_index = faiss.deserialize_index(index_array)

    except Exception as error:
        raise RuntimeError(
            "FAISS 인덱스를 불러오지 못했습니다.\n\n"
            "파일이 손상됐거나 현재 설치된 FAISS 버전과 "
            "인덱스를 생성한 환경이 호환되지 않을 수 있습니다."
        ) from error

    return loaded_index


# =========================
# 임베딩 모델 로드
# =========================
@st.cache_resource(show_spinner=False)
def load_embedding_model(model_id: str):
    """SentenceTransformer 모델을 CPU 환경으로 불러온다."""

    try:
        return SentenceTransformer(
            model_id,
            device="cpu",
        )

    except Exception as error:
        raise RuntimeError(
            "SentenceBERT 모델을 불러오지 못했습니다.\n\n"
            f"모델: {model_id}\n\n"
            "인터넷 연결 또는 requirements.txt의 "
            "sentence-transformers 설치 여부를 확인하세요."
        ) from error


# =========================
# 초기 자원 로드
# =========================
try:
    with st.spinner("도서 데이터와 추천 모델을 불러오고 있습니다..."):
        df_books = load_books(DATA_PATH)
        faiss_index = load_faiss_index(INDEX_PATH)
        embedding_model = load_embedding_model(MODEL_ID)

except Exception as error:
    st.error("추천 시스템 초기화에 실패했습니다.")
    st.exception(error)
    st.stop()


# =========================
# 데이터-인덱스 정합성 검증
# =========================
if len(df_books) != faiss_index.ntotal:
    st.error(
        "도서 데이터와 FAISS 인덱스의 개수가 일치하지 않습니다.\n\n"
        f"- 도서 데이터: {len(df_books):,}권\n"
        f"- FAISS 벡터: {faiss_index.ntotal:,}개\n\n"
        "동일한 도서 데이터로 생성한 FAISS 인덱스인지 확인해야 합니다."
    )
    st.stop()


if faiss_index.d <= 0:
    st.error("FAISS 인덱스의 벡터 차원이 올바르지 않습니다.")
    st.stop()


# =========================
# 추천 함수
# =========================
def recommend_books(
    query_texts: list[str],
    top_k: int = 10,
) -> pd.DataFrame:
    """
    사용자가 입력한 여러 취향 문장을 평균 임베딩하여
    FAISS 기반 유사 도서를 추천한다.
    """

    clean_queries = [
        str(query).strip()
        for query in query_texts
        if str(query).strip()
    ]

    if not clean_queries:
        return pd.DataFrame()

    query_embeddings = embedding_model.encode(
        clean_queries,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    query_embeddings = np.asarray(
        query_embeddings,
        dtype=np.float32,
    )

    user_vector = query_embeddings.mean(
        axis=0,
        keepdims=True,
    ).astype(np.float32)

    vector_norm = np.linalg.norm(user_vector)

    if not np.isfinite(vector_norm) or vector_norm == 0:
        return pd.DataFrame()

    user_vector /= vector_norm

    if user_vector.shape[1] != faiss_index.d:
        raise ValueError(
            "입력 임베딩 차원과 FAISS 인덱스 차원이 일치하지 않습니다.\n\n"
            f"- 입력 임베딩: {user_vector.shape[1]}차원\n"
            f"- FAISS 인덱스: {faiss_index.d}차원\n\n"
            "FAISS 인덱스를 생성할 때 사용한 모델과 "
            "현재 MODEL_ID가 동일한지 확인하세요."
        )

    search_k = min(
        max(top_k, 1),
        faiss_index.ntotal,
    )

    similarities, indices = faiss_index.search(
        user_vector,
        search_k,
    )

    valid_positions = [
        position
        for position, item_index in enumerate(indices[0])
        if 0 <= int(item_index) < len(df_books)
    ]

    if not valid_positions:
        return pd.DataFrame()

    valid_indices = [
        int(indices[0][position])
        for position in valid_positions
    ]

    valid_similarities = [
        float(similarities[0][position])
        for position in valid_positions
    ]

    result = df_books.iloc[valid_indices].copy()

    result["similarity"] = valid_similarities

    preferred_columns = [
        "title",
        "author_clean",
        "author",
        "cat_main",
        "cat_mid",
        "category",
        "publisher",
        "pubDate",
        "cover_url",
        "link",
        "description",
        "similarity",
    ]

    result_columns = [
        column
        for column in preferred_columns
        if column in result.columns
    ]

    result = result[result_columns]
    result = result.drop_duplicates(
        subset=["title"],
        keep="first",
    )

    result = result.sort_values(
        by="similarity",
        ascending=False,
    )

    return result.head(top_k).reset_index(drop=True)


# =========================
# 보조 함수
# =========================
def get_first_available(
    row: pd.Series,
    columns: list[str],
    default: str = "",
) -> str:
    """여러 후보 컬럼 중 값이 존재하는 첫 번째 값을 반환한다."""

    for column in columns:
        if column not in row.index:
            continue

        value = row.get(column)

        if pd.notna(value) and str(value).strip():
            return str(value).strip()

    return default


# =========================
# 화면 구성
# =========================
st.title("📖 취향에 맞는 책 추천받기")

st.markdown(
    """
좋아하는 책이나 원하는 책의 분위기를 입력하면  
**제목·저자·카테고리·소개문의 의미 유사도**를 분석해 추천합니다.
"""
)

with st.expander("추천 시스템 정보"):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("추천 대상 도서", f"{len(df_books):,}권")

    with col2:
        st.metric("임베딩 차원", f"{faiss_index.d:,}")

    with col3:
        st.metric("임베딩 모델", "ko-sroberta")

st.divider()


# =========================
# 입력 폼
# =========================
with st.form("recommendation_form"):
    query_1 = st.text_input(
        "첫 번째 책 또는 취향",
        placeholder=(
            "예: 달러구트 꿈 백화점 - "
            "따뜻하고 신비로운 힐링 소설"
        ),
    )

    query_2 = st.text_input(
        "두 번째 책 또는 취향",
        placeholder=(
            "예: 불편한 편의점 - "
            "사람 냄새 나는 따뜻한 이야기"
        ),
    )

    query_3 = st.text_input(
        "세 번째 책 또는 취향",
        placeholder=(
            "예: 인생의 선택과 성장을 다룬 판타지 소설"
        ),
    )

    top_k = st.slider(
        "추천 도서 수",
        min_value=5,
        max_value=20,
        value=10,
        step=5,
    )

    submitted = st.form_submit_button(
        "책 추천받기",
        type="primary",
        use_container_width=True,
    )


# =========================
# 추천 실행
# =========================
if submitted:
    query_texts = [
        query_1,
        query_2,
        query_3,
    ]

    clean_query_texts = [
        query.strip()
        for query in query_texts
        if query and query.strip()
    ]

    if not clean_query_texts:
        st.warning(
            "책 제목이나 원하는 분위기를 한 개 이상 입력해주세요."
        )

    else:
        try:
            with st.spinner("취향을 분석하고 있습니다..."):
                recommendations = recommend_books(
                    query_texts=clean_query_texts,
                    top_k=top_k,
                )

        except Exception as error:
            st.error("추천 결과 생성 중 오류가 발생했습니다.")
            st.exception(error)

        else:
            if recommendations.empty:
                st.warning(
                    "추천 결과를 찾지 못했습니다. "
                    "다른 책이나 취향 문장을 입력해보세요."
                )

            else:
                st.divider()
                st.subheader("📚 추천 결과")

                st.caption(
                    "유사도는 입력한 취향 문장과 도서 콘텐츠의 "
                    "의미적 유사성을 나타냅니다."
                )

                for rank, row in recommendations.iterrows():
                    cover_column, info_column = st.columns(
                        [1, 5],
                        vertical_alignment="top",
                    )

                    with cover_column:
                        cover_url = get_first_available(
                            row,
                            ["cover_url"],
                        )

                        if cover_url:
                            try:
                                st.image(
                                    cover_url,
                                    width=130,
                                )
                            except Exception:
                                st.caption("표지 이미지 없음")
                        else:
                            st.caption("표지 이미지 없음")

                    with info_column:
                        title = get_first_available(
                            row,
                            ["title"],
                            "제목 없음",
                        )

                        author = get_first_available(
                            row,
                            ["author_clean", "author"],
                            "저자 정보 없음",
                        )

                        category = get_first_available(
                            row,
                            ["cat_mid", "cat_main", "category"],
                            "분류 정보 없음",
                        )

                        publisher = get_first_available(
                            row,
                            ["publisher"],
                            "출판사 정보 없음",
                        )

                        pub_date = get_first_available(
                            row,
                            ["pubDate"],
                            "출간일 정보 없음",
                        )

                        description = get_first_available(
                            row,
                            ["description"],
                        )

                        similarity = float(
                            row.get("similarity", 0.0)
                        )

                        st.markdown(
                            f"### {rank + 1}. {title}"
                        )

                        st.write(f"**저자:** {author}")
                        st.write(f"**분류:** {category}")
                        st.write(
                            f"**출판사·출간일:** "
                            f"{publisher} · {pub_date}"
                        )

                        progress_value = max(
                            0.0,
                            min(similarity, 1.0),
                        )

                        st.progress(
                            progress_value,
                            text=f"콘텐츠 유사도 {similarity:.3f}",
                        )

                        if description:
                            with st.expander("도서 소개 보기"):
                                st.write(description)

                        link = get_first_available(
                            row,
                            ["link"],
                        )

                        if link:
                            st.link_button(
                                "알라딘에서 보기",
                                link,
                            )

                    st.divider()