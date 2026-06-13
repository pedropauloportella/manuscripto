# Dockerfile
# Propósito: Configurar o ambiente de execução para a aplicação FastAPI dentro de um contêiner Docker.
# Este arquivo é usado para construir a imagem Docker da aplicação Python.
# Variáveis de ambiente importantes: Nenhuma diretamente neste arquivo, mas a aplicação usa variáveis do .env.

# Usa uma imagem oficial do Python como base
FROM python:3.11-slim-bookworm

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instala dependências de sistema necessárias para alguns pacotes Python (ex: psycopg2 para PostgreSQL)
# build-essential e libpq-dev são para compilação de pacotes como psycopg2
# gcc é geralmente incluído no build-essential, mas explicitado para clareza
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de requisitos e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação para o contêiner
COPY . .

# Garante que o diretório raiz esteja no path do Python para encontrar o módulo 'app'
ENV PYTHONPATH=/app

# Define o comando padrão para rodar a aplicação usando Uvicorn
# --host 0.0.0.0 é essencial para que a aplicação seja acessível de fora do contêiner
# --port 8000 define a porta interna
# --reload habilita o recarregamento automático do código em desenvolvimento (útil com volumes montados)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
