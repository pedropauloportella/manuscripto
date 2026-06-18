### Manuscripto

Sistema de gestão editorial e marketplace de coautoria acadêmica. O Manuscripto facilita o ciclo de vida de publicações (livros, artigos, capítulos) e permite que editores gerenciem vagas de coautoria integradas a um ecossistema de pagamentos.

## Objetivo do MVP

1.  **Perfis Acadêmicos:** Identificação via ORCID/Google com dados de formação e links sociais.
2.  **Marketplace de Coautoria:** Criação de vagas para participação em obras acadêmicas.
3.  **Pagamento Automatizado:** Integração com Mercado Pago e vinculação automática de autores.
4.  **Painel Administrativo:** Gestão de usuários, publicações e monitoramento de saúde do sistema.

## Funcionalidades Principais

*   **Autenticação Segura:** Login via Supabase Auth (Google, ORCID, E-mail/Senha).
*   **Perfis Dinâmicos:** URLs baseadas em UUID (`/profile/:id`) para referência em citações e obras.
*   **Níveis de Acesso:**
    *   *Admin:* Controle total de usuários e sistema.
    *   *Editor:* Gestão de publicações e ofertas de vagas.
    *   *Autor:* Gestão de perfil e visualização de obras adquiridas.
*   **Dashboard Admin:** Monitoramento em tempo real do status da API e Banco de Dados.

## Stack Tecnológica

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy (ORM) + Alembic, Pydantic, Uvicorn
- **Banco de Dados:** (supabase)PostgreSQL
- **Cache/Mensageria:** Redis
- **Armazenamento de Arquivos:** Supabase Storage (via S3 API)
- **Frontend:** React (aplicação separada)
- **Pagamento:** Mercado Pago (SDK Integration)
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

### 2. Configuração Técnica

*   **JWT Supabase:** O backend valida os tokens usando o segredo do Supabase (`SUPABASE_JWT_SECRET`).
*   **CORS:** Configurado para aceitar requisições de `http://localhost:5173`.
*   **Banco de Dados:** PostgreSQL hospedado no Supabase, gerenciado via SQLAlchemy.

### 3. Comandos Úteis (Docker)

**Subir ambiente:**
```bash
docker compose -f docker-compose.dev.yml up --build -d
```

**Migrações de Banco:**
```bash
docker compose -f docker-compose.dev.yml exec app alembic revision --autogenerate -m "Descricao"
docker compose -f docker-compose.dev.yml exec app alembic upgrade head
```

**Logs:**
```bash
tail -f logs/app/app.log
```

---
*Manuscripto - Ciência Conectada.*

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

Para que o sistema reconheça um usuário como administrador (via `app_metadata` no JWT), siga estes passos:

1. **Criar Usuário no Supabase:**
   Vá ao Dashboard do Supabase -> **Authentication** -> **Users** -> **Add User** e crie o usuário (ex: `admin@example.com`).

2. **Promover a Admin (SQL Editor):**
   Execute o seguinte comando no **SQL Editor** do Supabase para injetar a flag de administrador diretamente nos metadados do JWT:
   ```sql
   UPDATE auth.users 
   SET raw_app_meta_data = raw_app_meta_data || '{"is_admin": true}' 
   WHERE email = 'admin@example.com';
   ```

3. **Criar no Banco Local (Opcional):**
   Caso seu backend ainda utilize uma tabela de usuários local para logs ou auditoria:
```bash
docker compose -f docker-compose.dev.yml exec app python scripts/create_admin.py --email admin@example.com --password adminpassword
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