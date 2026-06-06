# app/core/config.py
# Propósito: Gerenciar as configurações da aplicação, carregando-as de variáveis de ambiente.
# Utiliza Pydantic BaseSettings para validação e carregamento simplificado.
# Variáveis de ambiente importantes: Todas as prefixadas no .env.example e as definidas aqui.

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Classe de configurações da aplicação.
    Carrega variáveis de ambiente e as valida usando Pydantic.
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Application Settings ---
    APP_NAME: str = "manuscripto"

    # --- JWT Settings ---
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Minutos para expiração do token de acesso

    # --- Database Settings ---
    DATABASE_URL: str

    # --- Redis Settings ---
    REDIS_URL: str

    # --- S3 Compatible Storage (MinIO for dev) ---
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    S3_BUCKET: str

    # --- Payment Gateway (MercadoPago Sandbox) ---
    MERCADOPAGO_ACCESS_TOKEN: str

    # --- OAuth2 Providers - ORCID ---
    ORCID_CLIENT_ID: str
    ORCID_CLIENT_SECRET: str
    ORCID_REDIRECT_URI: str
    # URLs específicas do ORCID, obtidas do README e do oauth2.py
    ORCID_AUTHORIZE_URL: str = "https://sandbox.orcid.org/oauth/authorize" # Usar sandbox para dev
    ORCID_TOKEN_URL: str = "https://sandbox.orcid.org/oauth/token"
    ORCID_PROFILE_URL: str = "https://api.sandbox.orcid.org/v3.0/latest/{{orcid_id}}/person" # Usar sandbox para dev
    ORCID_SCOPES: str = "/authenticate /read-limited" # Escopos mínimos para autenticação

    # --- OAuth2 Providers - Google ---
    GOOGLE_OAUTH_CLIENT_ID: Optional[str] = None
    GOOGLE_OAUTH_CLIENT_SECRET: Optional[str] = None
    GOOGLE_OAUTH_REDIRECT_URI: Optional[str] = None

# Cria uma instância das configurações para ser usada em toda a aplicação
settings = Settings()
