"""
설명 생성 로컬 폴백
API 서버 없이 Streamlit 프로세스에서 직접 LLM 호출
"""
import os
import streamlit as st


def _get_api_key():
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        return os.getenv("GOOGLE_API_KEY")


@st.cache_resource(show_spinner=False)
def _get_explainer():
    import sys
    sys.path.append(".")
    from api.explainer import RecommendationExplainer
    return RecommendationExplainer(api_key=_get_api_key())


def explain_local(payload: dict) -> dict:
    explainer = _get_explainer()
    return explainer.explain(
        query_summary=payload["query_summary"],
        books=payload["books"],
        path=payload["path"],
    )