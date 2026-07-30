"""
장르 태그 기반 메타데이터 필터

FAISS 벡터 검색은 유사도만 계산하므로 "소설만" 같은 조건을 보장하지 못한다.
사용자가 장르 태그를 선택한 경우 검색 결과에 카테고리 필터를 후처리로 적용한다.

전략:
  - 장르·서브장르 태그만 필터에 사용 (분위기 태그는 임베딩에만 반영)
  - over-fetch 후 필터링해 결과 수를 확보
  - 필터 결과가 부족하면 완화 (graceful degradation)
"""
from typing import List, Optional, Set, Tuple

import pandas as pd

# 태그 -> 실제 cat_main 값 매핑
GENRE_TO_CATEGORIES = {
    # 장르
    "소설": ["소설/시/희곡", "만화/라이트노벨"],
    "시": ["소설/시/희곡"],
    "에세이": ["에세이"],
    "자기계발": ["자기계발"],
    "인문": ["인문학", "사회과학", "역사"],
    "과학": ["과학"],
    # 서브장르 (소설 계열로 한정)
    "판타지": ["소설/시/희곡", "만화/라이트노벨"],
    "SF": ["소설/시/희곡", "만화/라이트노벨"],
    "추리": ["소설/시/희곡", "만화/라이트노벨"],
    "로맨스": ["소설/시/희곡", "만화/라이트노벨"],
}

# 필터에 사용하지 않는 태그 (임베딩에만 반영)
#   힐링, 성장 - 에세이/자기계발에도 걸쳐 있어 한정하면 손실이 큼
#   따뜻한, 묵직한, 유쾌한, 감동적인, 깊이있는, 긴장감 - 정서는 장르와 독립


def resolve_allowed_categories(tags: List[str]) -> Optional[Set[str]]:
    """
    선택된 태그에서 허용 카테고리 집합을 도출.
    매핑되는 태그가 하나도 없으면 None (필터 미적용)
    """
    allowed: Set[str] = set()
    for tag in tags:
        cats = GENRE_TO_CATEGORIES.get(tag)
        if cats:
            allowed.update(cats)
    return allowed or None


def apply_category_filter(
    results: pd.DataFrame,
    allowed: Optional[Set[str]],
    top_k: int,
) -> Tuple[pd.DataFrame, bool, bool]:
    """
    카테고리 필터 적용

    Returns:
        (결과 DataFrame, 필터 적용 여부, 완화 여부)
    """
    if not allowed:
        return results.head(top_k), False, False

    filtered = results[results["cat_main"].isin(allowed)]
    min_results = max(3, top_k // 2)

    if len(filtered) >= min_results:
        return filtered.head(top_k), True, False

    # 완화: 필터 결과가 부족하면 나머지를 유사도 순으로 채움
    remaining = results[~results.index.isin(filtered.index)]
    combined = pd.concat([filtered, remaining]).head(top_k)
    return combined, True, True