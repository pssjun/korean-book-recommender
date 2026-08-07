FROM python:3.12-slim

# PORT를 환경 변수로 받아 로컬(8000)과 Cloud Run(8080) 양쪽에 대응
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/app/.cache/huggingface \
    PORT=8000

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-api.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-api.txt

# 빌드 시점 모델 사전 다운로드 (Cold Start 완화)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"

COPY api/ ./api/
COPY data/ ./data/
COPY models/ ./models/

# 셸 형식으로 작성해 ${PORT} 확장이 동작하도록 함
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE 8000

CMD exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT}