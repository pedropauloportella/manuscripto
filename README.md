### Manuscripto

Sistema de gestão editorial para publicações acadêmicas que cobre o ciclo: submissão, revisão, edição, versionamento, publicação e distribuição, com suporte a livros, capítulos, dossiês e artigos. 

Inclui portal para autores, revisores e editores, catálogo público, para facilitar fluxos editoriais configuráveis e automação de operações.

## Objetivo do MVP

Este MVP visa permitir que um editor crie vagas numa publicação, exiba-as no catálogo, e que um usuário faça um pagamento usando o MercadoPago como Gateway. A confirmação via webhook deve vincular o comprador como coautor. Inclui login social via ORCID (OAuth2) e Google.

## Stack Tecnológica

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy (ORM) + Alembic, Pydantic, Uvicorn
- **Banco de Dados:** PostgreSQL
- **Cache/Mensageria:** Redis
- **Armazenamento de Arquivos:** Supabase Storage (via S3 API)
- **Frontend:** React (aplicação separada)
- **Pagamento:** MercadoPago (sandbox)
- **Autenticação:** JWT, OAuth2 (ORCID, Google)

## Estrutura do Projeto

A seguir, a estrutura básica de diretórios e arquivos que será construída para o projeto:

```
.
├── app/                      # Código fonte da aplicação FastAPI
│   ├── api/                  # Módulos com as rotas da API
│   ├── auth/                 # Lógica de autenticação e OAuth
│   ├── core/                 # Configurações e utilitários da aplicação
│   ├── db/                   # Configuração do banco de dados e modelos SQLAlchemy
│   ├── services/             # Lógica de negócio e integrações
│   ├── main.py               # Ponto de entrada da aplicação FastAPI
│   └── __init__.py           # Marca o diretório como um pacote Python
├── alembic/                  # Diretório de migrações do Alembic
│   ├── versions/             # Arquivos de migração gerados
│   └── env.py                # Script de ambiente do Alembic
│   └── script.py.mako        # Template para novas migrações
├── scripts/                  # Scripts utilitários (e.g., criação de admin, importação)
├── tests/                    # Testes unitários e de integração
├── frontend/                 # (Placeholder) Diretório para a aplicação React (desenvolvimento separado)
├── .env.example              # Exemplo de variáveis de ambiente
├── Dockerfile                # Configuração para construção da imagem Docker da aplicação
├── docker-compose.dev.yml    # Configuração do Docker Compose para ambiente de desenvolvimento
├── requirements.txt          # Dependências Python
├── alembic.ini               # Configuração do Alembic
└── README.md                 # Este arquivo
```

## Configuração do Ambiente (Desenvolvimento)

### 1. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto, copiando e preenchendo as variáveis de `.env.example`:

```bash
cp .env.example .env
```

Preencha as variáveis `ORCID_CLIENT_ID`, `ORCID_CLIENT_SECRET`, `MERCADOPAGO_ACCESS_TOKEN`, `JWT_SECRET` e `GOOGLE_OAUTH_*` com os valores corretos.

### 2. Configuração de Autenticação (Supabase & OAuth)

1.  **JWT do Supabase:** Obtenha a `JWT Secret` em *Settings -> API* no painel do Supabase e adicione ao `.env` como `SUPABASE_JWT_SECRET`. Isso permite que o FastAPI valide tokens emitidos pelo Supabase.
2.  **ORCID OAuth:** Registre uma aplicação em ORCID Developer. Configure a Redirect URI para `{URL_DA_API}/api/v1/auth/orcid/callback`.
3.  **Google OAuth:** Configure as credenciais no Google Cloud Console e aponte a Redirect URI para `{URL_DA_API}/api/v1/auth/google/callback`.

### 3. Configuração do MercadoPago (Webhook)

Para receber notificações de pagamento em ambiente local:
1.  Use o **ngrok** para expor a porta `8000`.
2.  Configure a `API_BASE_URL` no `.env` com a URL do ngrok.
3.  O endpoint de Webhook é `/api/v1/payments/webhook`.

### 4. Armazenamento (S3)

As chaves de acesso ao S3 devem ser obtidas no painel do Supabase em *Project Settings -> Storage*.

### 5. Executando com Docker Compose

Certifique-se de ter o Docker Desktop instalado e rodando. No Windows, prefira usar o PowerShell.

```bash
# 1. Inicia os serviços (O parâmetro -f é obrigatório para arquivos com nomes customizados)
docker compose -f docker-compose.dev.yml up --build -d

# 2. Verifique se os contêineres estão "Up" (rodando)
docker compose -f docker-compose.dev.yml ps
```

### 5. Migrações do Banco de Dados

Após os contêineres estarem rodando, aplique as migrações do banco de dados:

```bash
# Execute este comando de dentro do contêiner da aplicação, ou usando um serviço separado no docker-compose
# Nota: O container 'app' deve estar rodando (docker compose ps)

# 1. Gere a revisão inicial (detecta automaticamente os modelos em app/models.py)
docker compose -f docker-compose.dev.yml exec app alembic revision --autogenerate -m "Initial migration"

# 2. Aplique a migração ao banco no Supabase
docker compose -f docker-compose.dev.yml exec app alembic upgrade head
```

### 6. Criar Usuário Administrador (Opcional)

Você pode usar um script para criar um usuário administrador inicial:

```bash
# Exemplo (assumindo o script na pasta 'scripts'):
docker-compose -f docker-compose.dev.yml exec app python scripts/create_admin.py --email admin@example.com --password adminpassword
```

### 7. Acesso à Aplicação

A API estará disponível em `http://localhost:8000`.

### 8. Rodando os Testes

Para rodar os testes, você pode executar de dentro do contêiner `app`:

```bash
docker-compose -f docker-compose.dev.yml exec app pytest
```


## Frontend

O frontend em React é uma aplicação separada e deve ser configurado e executado conforme suas próprias instruções (normalmente `npm install` e `npm start` em seu próprio diretório). Ele interagirá com esta API.


exec app python scripts/create_admin.py --email admin@example.com --password adminpassword