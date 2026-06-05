#!/usr/bin/env bash

# Script para criar a estrutura de diretórios e arquivos iniciais para o projeto manuscripto.
# Este script configura a base para o desenvolvimento do backend FastAPI e prepara placeholders.
# Desenvolvido por: Pedro Paulo Neves Portella

set -euo pipefail

# Função para criar diretórios de forma robusta
create_dirs() {
    echo "Criando diretórios..."
    mkdir -p app/api
    mkdir -p app/auth
    mkdir -p app/core # Adicionado core/ para configurações e utilitários
    mkdir -p app/db   # Adicionado db/ para configuração do banco e modelos
    mkdir -p app/services
    mkdir -p alembic/versions
    mkdir -p frontend
    mkdir -p scripts
    mkdir -p tests
}

# Função para criar arquivos placeholder
create_files() {
    echo "Criando arquivos placeholder..."
    # Arquivos na raiz do projeto
    touch .env.example .gitignore Dockerfile README.md alembic.ini pyproject.toml docker-compose.dev.yml requirements.txt

    # Arquivos em app/
    touch app/__init__.py app/main.py
    touch app/core/config.py app/db/base.py app/db/session.py app/db/base_class.py # Ajustado para estrutura mais granular
    touch app/schemas.py app/models.py # Models e Schemas agora em arquivos próprios

    # app/api
    touch app/api/__init__.py app/api/auth.py app/api/catalog.py app/api/publications.py app/api/vagas.py app/api/compras.py app/api/webhooks.py app/api/s3_uploads.py

    # app/auth
    touch app/auth/__init__.py app/auth/router.py app/auth/security.py app/auth/dependencies.py

    # app/services
    touch app/services/__init__.py app/services/mercado_pago.py app/services/redis_service.py app/services/s3_service.py

    # alembic
    touch alembic/env.py alembic/script.py.mako
    touch alembic/versions/.gitkeep # Para garantir que a pasta 'versions' seja versionada mesmo vazia

    # scripts
    touch scripts/create_admin.py scripts/import_csv.py

    # tests
    touch tests/__init__.py tests/conftest.py tests/test_auth.py tests/test_purchase_flow.py tests/test_api.py

    # Frontend placeholder
    echo "Arquivos do React/Vite serão gerados mais tarde." > frontend/README.md
}

# Main execution
main() {
    create_dirs
    create_files
    echo "Estrutura de diretórios e arquivos iniciais criada com sucesso."
    echo "Lembre-se de preencher o .env.example e executar 'cp .env.example .env'."
}

# Executa a função principal
main