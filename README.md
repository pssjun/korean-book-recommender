# 📚 한국 도서 하이브리드 추천 시스템

[![Docker Build & API Test](https://github.com/pssjun/korean-book-recommender/actions/workflows/docker-build.yml/badge.svg)](https://github.com/pssjun/korean-book-recommender/actions/workflows/docker-build.yml)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-4B8BBE)
![Gemini](https://img.shields.io/badge/Gemini-RAG-8E75B2?logo=google&logoColor=white)

> **콘텐츠 임베딩과 협업 필터링을 결합한 추천 모델을 API로 서빙하고, 컨테이너화·CI·RAG까지 확장한 End-to-End ML 서비스**

한국 도서 6,974권을 SentenceBERT로 임베딩하고 FAISS로 검색하는 추천 엔진을 FastAPI로 서빙합니다.
Docker로 컨테이너화했으며, GitHub Actions가 push마다 컨테이너를 실제로 기동해 7가지 항목을 검증합니다.
추천 근거 설명은 Gemini를 활용한 RAG로 생성합니다.

🔗 **[Live Demo](https://korean-book-recommender.streamlit.app/)** · **[프로젝트 상세 리포트](./BOOK_OVERVIEW_KOR.md)**

---

## 목차

- [📌 한눈에 보기](#-한눈에-보기)
- [🎯 핵심 성과](#-핵심-성과)
- [🛠 기술 스택](#-기술-스택)
- [⚡ 빠른 시작](#-빠른-시작)
- [🏗 시스템 아키텍처](#-시스템-아키텍처)
- [🔌 API 개요](#-api-개요)
- [🔄 아키텍처 전환: Streamlit 단일 앱 → API 분리](#-아키텍처-전환-streamlit-단일-앱--api-분리)
- [🐳 Docker 구성](#-docker-구성)
- [🔐 시크릿 관리](#-시크릿-관리)
- [✅ CI 통합 테스트](#-ci-통합-테스트)
- [🤖 RAG 기반 추천 이유 설명](#-rag-기반-추천-이유-설명)
- [🏷 벡터 검색의 한계와 메타데이터 필터링](#-벡터-검색의-한계와-메타데이터-필터링)
- [🔗 외부 의존성 관리](#-외부-의존성-관리)
- [🔍 트러블슈팅: 데이터-인덱스 정합성](#-트러블슈팅-데이터-인덱스-정합성)
- [💡 주요 발견](#-주요-발견)
- [⚠️ 한계 및 향후 개선](#️-한계-및-향후-개선)
- [📂 프로젝트 구조](#-프로젝트-구조)

---

## 📌 한눈에 보기

| | |
|---|---|
| **문제** | 국내 서점 추천은 인기순 위주이며 신규 유저 온보딩이 부재. 국내 도서의 유저-상호작용 데이터는 비공개 |
| **접근** | 콘텐츠 임베딩(실서비스)과 협업 필터링(방법론 검증)을 분리한 이중 트랙 하이브리드 |
| **서빙** | FastAPI + Docker. 모델은 컨테이너 기동 시 1회 로딩 후 메모리 상주 |
| **확장** | Gemini 기반 RAG로 추천 근거 설명 생성, 장르 메타데이터 필터링 |
| **검증** | CI에서 컨테이너를 실제 기동해 7가지 항목 자동 확인 |
| **기간/인원** | 2025.01 – 2025.08 (8개월) / 개인 프로젝트 |

---

## 🎯 핵심 성과

### 모델링

- 한국 도서 **6,974권** 콘텐츠 임베딩(SentenceBERT + FAISS) 파이프라인 구축
- 협업 필터링 **6종 벤치마크**(Popularity / User-CF / Item-CF / SVD / ALS / Neural CF) 수행
- **ALS가 Baseline 대비 NDCG@10 +72.4%** 달성
- Neural CF가 Popularity 수준으로 저조한 결과를 원인 분석과 함께 리포트 (Rendle et al. 2020 재현)

### 서빙 & 인프라

- Streamlit 단일 앱 → **FastAPI API 서버로 분리**, 추천 로직을 재사용 가능한 구조로 전환
- **Docker 컨테이너화** — 빌드 시점 모델 사전 다운로드로 Cold Start 제거, 레이어 캐싱 최적화
- **Pydantic 스키마 검증** — 범위를 벗어난 입력이 모델에 도달하기 전 422로 차단
- **관측 가능성** — 요청 로깅 미들웨어, `X-Process-Time-Ms` 헤더, 정합성까지 노출하는 `/health`
- **이중화 폴백** — API 장애 시 프론트엔드 로컬 추론으로 자동 전환

### LLM & 검색 품질

- **RAG 기반 추천 이유 설명** — Gemini Flash-Lite 연동, 캐싱·폴백·환각 억제 설계 포함
- **메타데이터 필터링** — 벡터 검색만으로 보장되지 않는 장르 조건을 후처리 필터로 해결
- **모델 폴백 체인** — 공급자 측 모델 지원 중단에 대응하는 다중 후보 + 기동 시 실호출 검증

### 품질 관리

- **CI 통합 테스트 구축** — push마다 이미지 빌드 후 컨테이너를 실제 기동하여 7가지 항목 검증
- **데이터-인덱스 정합성 문제 발견 및 해결** — 헬스체크로 배포 직후 탐지, fail-fast 가드 + CI 검증으로 재발 방지

---

## 🛠 기술 스택

- **언어**: Python 3.12
- **데이터 수집**: `aiohttp` (비동기 병렬), `requests`
- **콘텐츠 임베딩**: `sentence-transformers`, `FAISS`
- **협업 필터링**: `implicit` (ALS), `scikit-learn` (SVD), `PyTorch` (NCF)
- **LLM / RAG**: `Gemini API`, `google-genai`
- **API 서빙**: `FastAPI`, `Uvicorn`, `Pydantic`
- **컨테이너 / CI**: `Docker`, `docker-compose`, `GitHub Actions`
- **데이터 처리**: `pandas`, `numpy`, `pyarrow`
- **프론트엔드**: `Streamlit` (Streamlit Cloud 배포)

---

## ⚡ 빠른 시작

```bash
git clone https://github.com/pssjun/korean-book-recommender.git
cd korean-book-recommender
```

### API 서버 (Docker)

```bash
# .env 파일에 GOOGLE_API_KEY 설정 후
docker compose up --build
# → http://localhost:8000/docs
```

`GOOGLE_API_KEY`가 없어도 추천 기능은 정상 동작합니다. RAG 설명 기능만 비활성화됩니다.

### 프론트엔드 (별도 터미널)

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### 인덱스 재생성

도서 데이터를 변경한 경우 인덱스를 다시 만들어야 합니다.

```bash
python scripts/build_index.py
```

---

## 🏗 시스템 아키텍처

프론트엔드와 추천 엔진을 분리하고, 추천 엔진을 컨테이너화했습니다.

```mermaid
flowchart LR
    subgraph FE["Frontend"]
        ST["Streamlit App<br/>UI 전담"]
    end

    subgraph API["FastAPI Container"]
        EP["/recommend/path-a<br/>/recommend/path-b<br/>/explain · /health"]
        SB["SentenceBERT<br/>쿼리 임베딩"]
        FS["FAISS Index<br/>6,974 vectors"]
        HB["하이브리드 스코어<br/>+ 장르 필터"]
        LLM["Gemini Flash-Lite<br/>추천 근거 설명"]
    end

    ST -->|HTTP POST| EP
    EP --> SB --> FS --> HB
    HB --> LLM
    HB -->|JSON Response| ST
    LLM -->|explanation| ST
```

**하이브리드 결합 공식**: `최종 점수 = α × 콘텐츠 유사도 + (1 − α) × 인기 신호`

- α = 1.0: 순수 콘텐츠 기반 (개인화 강조)
- α = 0.0: 순수 인기순
- α = 0.7 (기본값): 개인화 우선 + 콜드 스타트 완화

---

## 🔌 API 개요

| Method | Endpoint | 설명 |
|---|---|---|
| `POST` | `/recommend/path-a` | 좋아하는 책 기반 추천 (취향 벡터 평균) |
| `POST` | `/recommend/path-b` | 태그 기반 추천 (콜드 스타트 대응, 장르 필터 적용) |
| `POST` | `/explain` | RAG 기반 추천 근거 설명 생성 |
| `GET` | `/tags` | 사용 가능한 취향 태그 목록 |
| `GET` | `/health` | 모델 로딩 상태, 데이터-인덱스 정합성, LLM 가용성 |

### 요청 예시

```bash
curl -X POST http://localhost:8000/recommend/path-b \
  -H "Content-Type: application/json" \
  -d '{"tags":["소설","힐링"],"top_k":5,"alpha":0.7}'
```

### 응답 예시

```json
{
  "path": "B",
  "alpha": 0.7,
  "query_summary": "소설, 힐링",
  "total_books_searched": 6974,
  "elapsed_ms": 42.7,
  "filter_applied": true,
  "filter_relaxed": false,
  "allowed_categories": ["만화/라이트노벨", "소설/시/희곡"],
  "results": [
    {
      "rank": 1,
      "title": "...",
      "author": "...",
      "category_main": "소설/시/희곡",
      "category_mid": "한국소설",
      "content_similarity": 0.7241,
      "popularity_score": 0.9200,
      "hybrid_score": 0.8034,
      "description": "..."
    }
  ]
}
```

Swagger UI(`/docs`)에서 브라우저로 직접 호출해볼 수 있습니다.

---

## 🔄 아키텍처 전환: Streamlit 단일 앱 → API 분리

### 전환 배경

초기에는 Streamlit 앱 하나에 모델 로딩·검색·UI를 모두 담았습니다. 프로토타입 단계에서는
빠르게 검증할 수 있었지만, 배포 후 세 가지 문제가 드러났습니다.

| 문제 | 상세 |
|---|---|
| Cold Start | 첫 요청 시 SentenceBERT 다운로드·로딩으로 수십 초 대기 |
| 메모리 제약 | Streamlit Cloud 무료 티어(1GB)에서 모델+인덱스 동시 상주 시 불안정 |
| 재사용성 부재 | 추천 로직이 UI 코드에 결합되어 다른 클라이언트에서 호출 불가 |

### 전환 전후 비교

| 항목 | Before (Streamlit 단일) | After (FastAPI + Docker) |
|---|---|---|
| 모델 로딩 | 요청 시점 로딩 (지연 발생) | 컨테이너 기동 시 1회 로딩 후 메모리 상주 |
| 추천 로직 위치 | UI 코드에 결합 | API 서버로 분리 (재사용 가능) |
| 입력 검증 | 수동 처리 | Pydantic 스키마 자동 검증 (422 응답) |
| 상태 확인 | 불가 | `/health` 엔드포인트 |
| 응답 시간 측정 | 불가 | 미들웨어로 전 요청 기록 + `X-Process-Time-Ms` 헤더 |

### 선택의 트레이드오프

**Streamlit 단일 앱을 유지하는 선택지**도 있었습니다. 배포 대상이 하나로 단순하고,
네트워크 홉이 없어 지연도 적습니다.

그럼에도 분리를 선택한 이유는, 이 프로젝트의 목표가 "동작하는 데모"가 아니라
**"모델을 서비스로 제공하는 구조"의 검증**이었기 때문입니다. 대신 분리로 생기는
비용은 다음과 같이 완화했습니다.

- **Cold Start**: Dockerfile 빌드 단계에서 모델을 사전 다운로드
- **운영 복잡도**: `docker-compose.yml`로 단일 명령 기동
- **가용성**: 아래 폴백 전략

### 폴백 전략: API 장애 시 로컬 추론

API 서버에 의존하는 구조에서는 서버 장애가 곧 서비스 전면 중단으로 이어집니다.
이를 완화하기 위해 프론트엔드에 **로컬 추론 폴백**을 구현했습니다.

```
사용자 요청
    ↓
API 호출 (2초 타임아웃)
    ├─ 성공 → API 결과 반환         (source: api)
    └─ 실패 → 앱 내부 추론으로 폴백  (source: local)
```

- API 서버와 **동일한 로직·동일한 인덱스**를 사용하므로 결과가 일치합니다
- 현재 실행 모드(API / 로컬)를 UI에 표시해 사용자가 상태를 인지할 수 있습니다
- 데모 환경에서는 API 서버 없이도 전체 기능을 체험할 수 있습니다

성능 면에서는 API 모드가 유리하지만(모델이 서버에 상주), 가용성을 우선해 이중화를
선택했습니다. 현재 Streamlit Cloud 데모는 API 서버가 클라우드에 배포되어 있지 않아
로컬 추론 모드로 동작합니다.

---

## 🐳 Docker 구성

### 주요 설계 결정

| 항목 | 결정 | 이유 |
|---|---|---|
| Base Image | `python:3.12-slim` | 표준 이미지 대비 용량 절감 |
| 레이어 순서 | 의존성 설치 → 코드 복사 | 코드 수정 시 패키지 재설치 생략 (캐시 활용) |
| 모델 처리 | 빌드 시점 사전 다운로드 | 컨테이너 첫 실행 시 Cold Start 제거 |
| 헬스체크 | `start_period` 90초 | 모델 로딩 + LLM 가용성 검증 시간 확보 |
| `.dockerignore` | Streamlit·노트북·원본 데이터 제외 | 이미지 용량 및 빌드 시간 절감 |

`start_period`를 넉넉히 둔 이유는 기동 시 두 가지 작업이 순차로 발생하기 때문입니다.
SentenceBERT 로딩(약 8초)과 LLM 모델 가용성 검증(후보별 실호출)이 더해집니다.

### 실행

```bash
docker build -t book-recommender-api .
docker run -p 8000:8000 --env-file .env book-recommender-api

# 또는
docker compose up --build
```

---

## 🔐 시크릿 관리

API 키를 이미지에 포함시키지 않고 런타임에 주입합니다.

```dockerfile
# 이렇게 하지 않는다 — 이미지 레이어에 영구히 남아 이미지 공유 시 유출
# ENV GOOGLE_API_KEY=...
```

```bash
docker run -p 8000:8000 --env-file .env book-recommender-api
```

로컬 개발에서는 `python-dotenv`로 `.env`를 자동 로딩하고, 컨테이너에서는 파일이
없으므로 무시된 뒤 `--env-file`로 전달된 값을 사용합니다.
`.env`와 `.streamlit/secrets.toml`은 `.gitignore`에 포함되어 있습니다.

---

## ✅ CI 통합 테스트

push마다 이미지를 빌드하고 **컨테이너를 실제로 기동**해 7가지 항목을 검증합니다.
빌드 성공 여부만 확인하는 것으로는 런타임 문제를 잡을 수 없기 때문입니다.

| 항목 | 검증 내용 |
|---|---|
| Build | Dockerfile이 정상 빌드되는가 |
| Health | 컨테이너가 뜨고 모델이 로딩되는가 |
| **Consistency** | **데이터 수와 인덱스 크기가 일치하는가** |
| Recommend A/B | 요청한 개수만큼 결과를 반환하는가 |
| Validation | 잘못된 입력(α=1.5)을 422로 거부하는가 |
| **Genre filter** | **장르 필터가 실제로 카테고리를 제한하는가** |
| **Explain contract** | **LLM이 없어도 200 + `explanation: null`을 반환하는가** |

### CI에 API 키를 넣지 않은 이유

의도적인 선택입니다.

- **할당량**: 무료 티어는 분당 15회. CI 실행마다 모델 검증 + 설명 생성이 발생하므로,
  연속 push 시 rate limit으로 CI가 실패합니다. 코드 문제가 아닌 이유로 실패하는 CI는
  신뢰를 잃습니다.
- **테스트의 본질**: CI가 검증할 것은 "우리 코드가 계약을 지키는가"입니다.
  LLM이 좋은 문장을 쓰는지는 CI의 관심사가 아닙니다.
- **결정론**: 외부 서비스에 의존하는 테스트는 불안정합니다.

대신 CI는 **LLM이 없을 때도 서비스가 정상 동작하는지** 검증합니다.
폴백 계약을 확인하는 것이 더 중요한 테스트입니다.

---

## 🤖 RAG 기반 추천 이유 설명

추천 결과에 "왜 이 책이 추천되었는지"를 자연어로 설명하는 기능을 추가했습니다.
기존 FAISS 검색을 Retrieval로 그대로 활용하고, 뒷단에 Generation을 붙인 구조입니다.

```mermaid
flowchart LR
    Q["사용자 입력"] --> R["Retrieval<br/>FAISS 유사도 검색"]
    R --> A["Augmented<br/>도서 메타데이터로<br/>컨텍스트 구성"]
    A --> G["Generation<br/>Gemini Flash-Lite"]
    G --> O["전체 추천 방향<br/>+ 개별 도서 3권<br/>내용·분위기·추천이유"]
```

### 설계 결정

| 항목 | 결정 | 이유 |
|---|---|---|
| 호출 시점 | 사용자가 버튼 클릭 시 | 추천은 40ms, LLM은 2~5초. 자동 생성하면 모든 사용자가 대기 |
| 컨텍스트 | 실제 도서 메타데이터만 | LLM 자체 지식을 쓰면 없는 줄거리를 생성할 위험 |
| temperature | 0.4 | 창의성보다 근거 충실도 우선 |
| 캐싱 | 입력 조합 단위 인메모리 캐시 | 지연·비용·rate limit 동시 완화 |
| 실패 처리 | 200 + `explanation: null` | 설명은 부가 기능이므로 추천 흐름을 중단시키지 않음 |

캐시 키에는 **모델 ID도 포함**합니다. 모델이 교체되면 설명 품질도 달라지므로,
이전 모델로 생성한 캐시가 그대로 반환되면 안 됩니다.

### 환각 억제

RAG를 붙이면 LLM이 검색 결과를 무시하고 자체 지식으로 답할 위험이 있습니다.
알라딘 소개문은 평균 132자로 짧아 이 위험이 특히 컸습니다.

세 가지로 대응했습니다.

- 컨텍스트에 **검색된 도서의 실제 메타데이터만** 포함 (제목, 저자, 분류, 소개문)
- 프롬프트에 "제공된 정보만 사용", "추측 금지" 명시
- **소개문이 부족한 책은 그렇다고 밝히도록** 지시 — 억지로 채우지 않는 것이 정직한 처리

LLM의 자체 지식을 허용하면 유명 도서의 설명은 풍부해지지만, 신간·무명 도서에서
환각이 발생합니다. 검색 결과를 근거로 삼는 것이 RAG의 전제이므로 전자를 택했습니다.

---

## 🏷 벡터 검색의 한계와 메타데이터 필터링

### 문제

Path B에서 "소설" 태그를 선택했는데 에세이가 결과에 포함되는 현상을 발견했습니다.

원인은 **FAISS가 필터가 아니라 유사도 검색**이라는 점입니다.

```
["소설", "힐링", "감동적인"]
  → 자연어 변환 → 임베딩 → 384차원 쿼리 벡터
  → FAISS: 이 벡터에 가까운 도서 반환
```

여기서 "소설"은 쿼리 벡터의 방향에 영향을 주는 요소일 뿐, `장르 = 소설`이라는 조건이
아닙니다. 그래서 힐링·감동이라는 정서가 강한 에세이가, 어둡고 무거운 소설보다 쿼리
벡터에 더 가까울 수 있습니다.

### 해결

검색 결과에 카테고리 필터를 후처리로 적용했습니다.

```
FAISS over-fetch (top_k × 10)
  → 하이브리드 스코어 정렬
  → 허용 카테고리 필터
  → 결과 부족 시 완화 (graceful degradation)
```

**어떤 태그를 필터로 쓸지**가 설계의 핵심이었습니다.

| 태그 유형 | 필터 | 판단 |
|---|---|---|
| 장르 (소설, 에세이, 인문, 과학) | ✅ | 사용자가 명확히 지정한 범주 |
| 서브장르 (판타지, SF, 추리, 로맨스) | ✅ 소설 계열로 한정 | 소설의 하위 분류 |
| 정서 (따뜻한, 묵직한, 감동적인) | ❌ | 어떤 장르에나 존재. 임베딩에만 반영 |
| 힐링, 성장 | ❌ | 에세이·자기계발에도 걸쳐 있어 한정하면 손실이 큼 |

"힐링"을 필터로 쓰면 좋은 에세이가 걸러지므로, 정서 태그는 벡터 유사도에만 맡기는
것이 적절하다고 판단했습니다.

필터 결과가 `max(3, top_k/2)` 미만이면 유사도 상위 도서로 채우고, 응답의
`filter_relaxed` 필드로 이를 알립니다. 결과가 없는 것보다 완화된 결과를 투명하게
알리는 편이 낫다고 보았습니다.

---

## 🔗 외부 의존성 관리

LLM 연동 과정에서 공급자 측 변경을 연달아 겪었습니다.

| 시점 | 변경 | 대응 |
|---|---|---|
| 개발 중 | 사용하던 모델의 지원 중단 → 429 할당량 오류 | 모델 ID를 폴백 체인으로 분리 |
| 키 발급 시 | API 키 형식 전환 | 문서 확인 후 신규 형식 적용 |
| 구현 중 | `google-generativeai` 패키지 지원 종료 | 후속 SDK `google-genai`로 마이그레이션 |

### 모델 폴백 체인

특정 모델에 강하게 결합하지 않도록 후보 목록을 두고, **초기화 시 실제 호출로 가용성을
검증**합니다.

```python
MODEL_CANDIDATES = [
    os.getenv("GEMINI_MODEL"),      # 환경 변수로 우선 지정 가능
    "gemini-flash-lite-latest",     # 별칭: 항상 최신 Flash-Lite
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
]
```

클라이언트 객체 생성만으로는 모델 가용성을 알 수 없습니다. 지원 중단된 모델도 객체는
정상 생성되고, **첫 사용 시점에야 429가 발생**했습니다. 그래서 초기화 단계에서 짧은
프롬프트로 한 번 호출해 검증합니다. 앱 시작 시 1회만 발생하는 비용입니다.

### 배운 점

외부 LLM API는 모델·인증·SDK 모든 계층에서 변경이 발생합니다. 버전을 코드에
하드코딩하지 않고 설정으로 분리하는 것, 그리고 외부 서비스 실패가 핵심 기능을
중단시키지 않도록 폴백을 두는 것이 실질적인 대비였습니다.

---

## 🔍 트러블슈팅: 데이터-인덱스 정합성

### 발견

컨테이너 배포 후 `/health` 응답에서 불일치를 확인했습니다.

```json
{ "status": "ok", "model_loaded": true, "index_size": 6881, "total_books": 6974 }
```

### 문제의 심각성

FAISS는 벡터를 **순번(index)** 으로 관리하고, 검색 결과의 순번으로 도서 메타데이터를
조회합니다(`books.iloc[indices]`). 따라서 인덱스와 데이터프레임의 행 순서가 1:1로
정확히 대응해야 합니다.

개수가 어긋났다는 것은 최소 93권이 검색 대상에서 누락되었거나, 최악의 경우 **행이 밀려
잘못된 도서 정보가 반환**될 수 있음을 의미했습니다. 성능 지표로는 드러나지 않고 조용히
잘못된 결과를 내보내는 유형의 결함입니다.

### 원인

임베딩 생성 시점의 원본 파일과 실제 서빙 파일이 서로 달라 정합성이 깨진 상태였습니다.

### 해결

**1. 재현 가능한 인덱스 빌드 스크립트** — 서빙에 사용하는 파일을 단일 기준(SSOT)으로
삼아 인덱스를 생성하고, 생성 과정에서 행 수를 검증합니다.

```bash
python scripts/build_index.py
```

**2. 기동 시 정합성 검증 (Fail Fast)** — API 로딩 단계에서 불일치를 감지하면 즉시
예외를 발생시켜 컨테이너가 뜨지 않도록 했습니다.

```python
if self.faiss_index.ntotal != len(self.books):
    raise RuntimeError(
        f"Data/Index mismatch: index={self.faiss_index.ntotal}, "
        f"books={len(self.books)}. Run scripts/build_index.py to rebuild."
    )
```

잘못된 추천을 조용히 서빙하는 것보다, 기동 시점에 명확히 실패하는 편이 안전하다고
판단했습니다.

**3. CI 검증 추가** — 동일한 문제가 배포 이전 단계에서 차단되도록 CI에 정합성 검증을
포함시켰습니다.

### 배운 점

헬스체크를 단순 생존 확인(`{"status": "ok"}`)이 아니라 **핵심 자원의 정합성까지
노출**하도록 설계한 덕분에, 사용자 신고 이전에 배포 직후 문제를 발견할 수 있었습니다.
모니터링 엔드포인트에 어떤 지표를 담을지가 실제 장애 탐지 시점을 좌우한다는 것을
확인한 사례입니다.

---

## 💡 주요 발견

1. **데이터 접근성 제약을 설계에 반영** — 국내 유저-상호작용 데이터 부재를 인정하고,
   콘텐츠 임베딩(실서비스)과 CF(방법론 검증)를 분리한 이중 트랙으로 해결
2. **딥러닝이 항상 우수하지 않다** — NCF가 Popularity 수준으로 저조.
   Rendle et al.(2020) 논문의 결론을 실증적으로 재현
3. **CF 단독의 근본적 한계** — 최고 성능(ALS)도 Precision@10 = 0.017 수준.
   콘텐츠 기반 하이브리드의 필요성을 정량적으로 뒷받침
4. **벡터 검색은 필터가 아니다** — 유사도 검색만으로는 범주 조건을 보장할 수 없어
   메타데이터 필터링이 필요함을 실증
5. **외부 의존성은 변한다** — 모델·인증·SDK 모든 계층에서 변경이 발생하므로
   설정 분리와 폴백이 필수

---

## ⚠️ 한계 및 향후 개선

### 모델링

- **개인화의 한계**: 유저 개별 이력 없이 콘텐츠 유사도 + 전체 평균 인기만 결합.
  실서비스에서는 유저 로그 축적 후 CF 재도입 필요
- **정량 평가 부재**: 국내 도서 상호작용 데이터가 없어 최종 하이브리드 시스템은
  정성 평가로만 검증
- **카테고리 세분화**: `cat_main`이 "소설/시/희곡"으로 묶여 있어 "시"만 선택해도
  소설이 함께 나옴. 더 세밀한 분류는 `cat_mid` 활용 필요

### 인프라

- **API 클라우드 미배포**: 컨테이너화는 완료했으나 클라우드 배포는 하지 않았습니다.
  현재 데모는 로컬 추론 폴백으로 동작합니다
- **캐시 휘발성**: 설명 캐시가 인메모리라 컨테이너 재시작 시 소실됩니다.
  프로덕션에서는 Redis 등 외부 캐시로 교체 필요
- **LLM 비용·지연**: 설명 생성이 2~5초 소요됩니다. 스트리밍 응답으로 체감 지연을
  줄이는 개선이 가능합니다

자세한 회고는 [프로젝트 상세 리포트](./BOOK_OVERVIEW_KOR.md)와 배포된 앱의
**[결론과 한계]** 페이지에서 확인할 수 있습니다.

---

## 📂 프로젝트 구조

```text
korean-book-recommender/
├── .github/workflows/
│   └── docker-build.yml           # CI: 빌드 + 컨테이너 통합 테스트
├── api/                           # FastAPI 추천 서버
│   ├── main.py                    # 엔드포인트, 미들웨어, lifespan
│   ├── recommender.py             # 추천 엔진 (모델·인덱스 관리, 정합성 검증)
│   ├── explainer.py               # RAG 설명 생성 (폴백 체인, 캐싱)
│   ├── genre_filter.py            # 장르 태그 → 카테고리 필터
│   └── schemas.py                 # Pydantic 요청/응답 스키마
├── src/                           # 프론트엔드 로컬 폴백
│   ├── local_recommender.py       # API 장애 시 직접 추론
│   └── local_explainer.py         # API 장애 시 직접 설명 생성
├── scripts/
│   └── build_index.py             # FAISS 인덱스 재생성 (정합성 검증 포함)
├── pages/                         # Streamlit 페이지 (API 클라이언트)
│   ├── 1_📖_책_추천받기.py
│   ├── 2_📊_협업_필터링_실험.py
│   └── 3_📝_결론과_한계.py
├── data/                          # 도서 메타데이터, 태그, 설정, CF 실험 결과
├── models/                        # FAISS 인덱스
├── notebooks/                     # 전체 분석 노트북 (Colab)
├── streamlit_app.py               # Streamlit 홈
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements-api.txt           # API 서버 의존성
└── requirements.txt               # Streamlit 의존성
```

---

## 📄 프로젝트 상세 리포트

문제 정의부터 가설 검증, 실험 결과까지 전체 연구 과정을 정리했습니다.

- [BOOK_OVERVIEW_KOR.md](./BOOK_OVERVIEW_KOR.md) — 개요 · 문제정의 · 가설설정 · 실험및검증 · 결론

---

## ⚠️ 참고 사항

- 브라우저 자동 번역 기능을 **끄고** 접속해 주세요 (한글 UI 왜곡 방지)
- 데모는 로컬 추론 모드로 동작하며, 첫 검색 시 모델 로딩으로 30초~1분 소요될 수 있습니다
- Streamlit Cloud 무료 티어 특성상 장시간 미사용 시 앱이 슬립 상태가 될 수 있습니다

---

## 📊 데이터 출처

- [알라딘 OpenAPI](https://blog.aladin.co.kr/openapi/popup/6695306)
- [Kaggle Book-Crossing Dataset](https://www.kaggle.com/datasets/arashnic/book-recommendation-dataset)

---

## 👤 About

- **작성자**: pssjun
- **프로젝트 유형**: 데이터 사이언스 / ML 엔지니어링 포트폴리오
- **관련 프로젝트**: [EV 충전소 수요 예측](https://github.com/pssjun/ev-charging-forecast) · [ESG 강화학습 재현연구](https://github.com/pssjun/esg-ppo-portfolio)