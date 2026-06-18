FROM python:3.11-slim AS builder
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
# Instalamos o pip-install em um diretório temporário e limpamos caches agressivamente
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
# Copiamos apenas as bibliotecas instaladas do usuário do estágio anterior
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# libpq5 é o único binário de sistema que o banco precisa
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Copiamos apenas os arquivos necessários do app, ignorando o resto via .dockerignore
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY alembic/ ./alembic/
COPY alembic.ini .