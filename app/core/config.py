from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Manuscripto"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "sua_chave_secreta_aqui"  # Mudar em produção
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 dias

    # Banco de Dados
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/manuscripto"

    # OAuth
    ORCID_CLIENT_ID: Optional[str] = None
    ORCID_CLIENT_SECRET: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    # MercadoPago
    MERCADOPAGO_ACCESS_TOKEN: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()