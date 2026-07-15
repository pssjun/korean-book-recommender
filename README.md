# 📚 한국 도서 하이브리드 추천 시스템

알라딘 API + SentenceBERT + FAISS 기반 개인화 도서 추천 시스템

## Live Demo
- (배포 URL 추후 추가)

## 기술 스택
- Python 3.12
- Streamlit
- sentence-transformers (jhgan/ko-sroberta-multitask)
- FAISS (Facebook AI Similarity Search)
- 알라딘 OpenAPI

## 프로젝트 구조
```
korean-book-recommender/
├── streamlit_app.py       # 홈 페이지
├── data/                  # 도서 데이터
├── models/                # FAISS 인덱스
├── src/                   # 재사용 모듈
├── pages/                 # 페이지들
└── requirements.txt
```