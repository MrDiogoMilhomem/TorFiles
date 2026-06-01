# =============================================================================
# TorFiles — Dockerfile
# Flask + Gunicorn | Python 3.13 Alpine
# Dependências externas: MariaDB + PostgreSQL (não incluídos nesta imagem)
# =============================================================================

FROM python:3.13-alpine AS base

# Metadados
LABEL maintainer="TorFiles"
LABEL description="TorFiles - Sistema seguro de compartilhamento de arquivos"

# Variáveis de ambiente base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# =============================================================================
# Estágio de build — instala dependências de compilação
# =============================================================================
FROM base AS builder

WORKDIR /build

# Dependências de sistema necessárias para compilar pacotes Python
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    mariadb-dev \
    pkgconfig

COPY requirements.txt .

# Instala dependências em diretório isolado (wheel cache)
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# =============================================================================
# Estágio final — imagem enxuta de produção
# =============================================================================
FROM base AS final

WORKDIR /app

# Apenas libs de runtime (sem gcc, sem headers)
RUN apk add --no-cache \
    libffi \
    libpq \
    mariadb-connector-c \
    tini

# Copia pacotes Python instalados do estágio builder
COPY --from=builder /install /usr/local

# Copia código da aplicação
COPY . .

# Cria usuário não-root para segurança
RUN addgroup -S torfiles && adduser -S torfiles -G torfiles \
    && chown -R torfiles:torfiles /app

USER torfiles

# Porta exposta (gunicorn bind)
EXPOSE 8000

# Variáveis de ambiente da aplicação
# ⚠️  Defina os valores reais via arquivo .env ou secrets do orquestrador
ENV LOCALDEV=false \
    LOCALDEV_DEBUG=false \
    LOCALDEV_HOST=0.0.0.0 \
    LOCALDEV_PORT=8000
# Variáveis obrigatórias — devem ser injetadas em tempo de execução:
# SECRET_KEY, ENCRYPTION_KEY, MARIADB_URL, POSTGRES_URL

# tini como init para reaper de processos zumbi
ENTRYPOINT ["/sbin/tini", "--"]

# Gunicorn: 2 workers por núcleo é o baseline recomendado
# Ajuste --workers conforme os recursos do host
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--threads", "2", \
     "--timeout", "120", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:app"]