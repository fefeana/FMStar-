# ==========================================
# 1. مرحلة بناء بوابة Go (Go Core Gateway)
# ==========================================
FROM golang:1.21-alpine AS go-builder

WORKDIR /app

# نسخ ملفات التبعيات وتنزيلها
COPY go.mod go.sum* ./
RUN go mod download || true

# نسخ باقي الأكواد وبناء الملف التنفيذي
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o go-gateway main.go

# ==========================================
# 2. بيئة التشغيل النهائية (Python + Go)
# ==========================================
FROM python:3.10-slim

# تثبيت الأدوات الأساسية
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# تثبيت مكتبات بايثون المطلوبة (FastAPI & Uvicorn)
RUN pip install --no-cache-dir fastapi uvicorn

# نسخ خادم Go المبنّي من المرحلة الأولى
COPY --from=go-builder /app/go-gateway /app/go-gateway

# نسخ باقي ملفات المشروع (تضمن وجود ai_service.py و index.html والمجلدات)
COPY . .

# إنشاء سكريبت تشغيل لتشغيل خدمة بايثون للذكاء الاصطناعي ثم خادم Go
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'python3 ai_service.py &' >> /app/start.sh && \
    echo 'exec /app/go-gateway' >> /app/start.sh && \
    chmod +x /app/start.sh

# فتح منفذ 8080 لتوافق Cloud Run و Render
EXPOSE 8080

# أمر البدء التلقائي في السحابة
CMD ["/app/start.sh"]
