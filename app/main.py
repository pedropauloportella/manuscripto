# app/main.py
# Propósito: Ponto de entrada principal da aplicação FastAPI.
# Variáveis de ambiente importantes: Carrega configurações de app/core/config.py e
# REDIS_URL para o RedisService.

import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

# Importar os routers
from app.api import auth, catalog, publications, vagas, compras, webhooks, s3_uploads
from app.auth.oauth2 import ORCIDOAuth2
from app.services.redis_service import RedisService

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.APP_NAME,
    allow_headers=["*"],
)

# Instancia o RedisService para uso nos eventos de startup/shutdown
redis_service = RedisService()

@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando a aplicação...")
    await redis_service.connect()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Encerrando a aplicação...")
    await redis_service.disconnect()

# Registrar os routers
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(catalog.router, prefix="/api/catalog", tags=["Catálogo"])
