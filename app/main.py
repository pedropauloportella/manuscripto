from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, HTTPException, status
from sqlalchemy import text
from app.api import auth, publications, payments, catalog, users
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para gestão editorial e coautoria do Manuscripto",
    version="0.1.0"
)

# Configuração de CORS para permitir que o frontend (Vite/React) acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, deve ser limitado ao domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão dos módulos de rotas
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Autenticação"])
app.include_router(catalog.router, prefix=f"{settings.API_V1_STR}/catalog", tags=["Catálogo Público"])
app.include_router(publications.router, prefix=f"{settings.API_V1_STR}/publications", tags=["Publicações"])
app.include_router(payments.router, prefix=f"{settings.API_V1_STR}/payments", tags=["Pagamentos"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Gestão de Usuários"])

from app.db.session import get_db # Import get_db
from sqlalchemy.orm import Session # Import Session

@app.get("/health", tags=["Health Check"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1")) # Simple query to check database connection
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database connection failed: {e}")

@app.get("/")
def root():
    return {
        "message": "Bem-vindo à API do Manuscripto",
        "docs": "/docs",
        "data_atual": datetime.now()
    }