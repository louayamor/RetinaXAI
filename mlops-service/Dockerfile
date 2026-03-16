FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM base AS runtime

WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .

RUN mkdir -p logs artifacts

ENTRYPOINT ["uvicorn", "mlops-service.main:app", "--host", "0.0.0.0", "--port", "8000"]