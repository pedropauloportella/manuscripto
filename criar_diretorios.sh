#!/usr/bin/env bash
set -euo pipefail

# Cria diretórios (inclui os pais quando necessário)
mkdir -p app/api
mkdir -p app/auth
mkdir -p app/services
mkdir -p alembic/versions
mkdir -p frontend
mkdir -p scripts
mkdir -p tests

# Cria arquivos na raiz
touch .env.example .gitignore Dockerfile README.md alembic.ini pyproject.toml docker-compose.dev.yml

# Arquivos em app/
touch app/__init__.py
touch app/config.py app/database.py app/exceptions.py app/main.py app/models.py app/schemas.py

# app/api
touch app/api/__init__.py
touch app/api/catalog.py app/api/compras.py app/api/publications.py app/api/s3_uploads.py app/api/vagas.py app/api/webhooks.py

# app/auth
touch app/auth/__init__.py
touch app/auth/router.py app/auth/security.py

# app/services
touch app/services/__init__.py
touch app/services/mercado_pago.py app/services/redis_service.py app/services/s3_service.py

# alembic
touch alembic/env.py
# placeholder .gitkeep em alembic/versions
touch alembic/versions/.gitkeep

# frontend placeholder note file
touch frontend/README.md
echo "Arquivos do React/Vite serão gerados mais tarde" > frontend/README.md

# scripts
touch scripts/create_admin.py scripts/import_csv.py

# tests
touch tests/conftest.py tests/test_purchase_flow.py

# Ajusta permissões executáveis para scripts Python se desejar (opcional)
chmod +x scripts/create_admin.py 2>/dev/null || true
chmod +x scripts/import_csv.py 2>/dev/null || true

echo "Estrutura criada com sucesso."