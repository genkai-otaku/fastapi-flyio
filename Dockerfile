FROM python:3.9 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN python -m venv .venv
COPY pyproject.toml ./
RUN .venv/bin/pip install .
FROM python:3.9-slim
WORKDIR /app

# Prisma CLI が Node を使うため libatomic1 が必要（slim には含まれない）
RUN apt-get update && apt-get install -y --no-install-recommends libatomic1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv .venv/
COPY . .

# ビルド時に Prisma クライアントを生成（schema の url 用にダミーでよい）
# Node Prisma CLI が generator として prisma-client-py を呼ぶため PATH に venv/bin を追加
ENV DATABASE_URL="postgresql://dummy:dummy@localhost:5432/dummy" \
    PATH="/app/.venv/bin:$PATH"
RUN /app/.venv/bin/python -m prisma generate

# Fly.io は internal_port 8080 でプロキシするため、0.0.0.0:8080 でリッスンする
CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

