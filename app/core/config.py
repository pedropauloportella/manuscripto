from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pydantic import model_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Manuscripto"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "sua_chave_secreta_aqui"  # Mudar em produção
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 dias
    API_BASE_URL: str = "http://localhost:8000" # URL para Webhooks

    # Banco de Dados
    # Nota: Use a porta 6543, sslmode=require e username 'postgres.[REF-PROJETO]' para o Supabase Pooler
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/editora"
    DATABASE_REF: Optional[str] = None
    DATABASE_PASSWORD: Optional[str] = None
    SUPABASE_JWT_SECRET: Optional[str] = None # Encontrado no painel do Supabase
    DATABASE_URL_TEST: Optional[str] = None

    # OAuth
    ORCID_CLIENT_ID: Optional[str] = None
    ORCID_CLIENT_SECRET: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    # MercadoPago
    MERCADOPAGO_ACCESS_TOKEN: Optional[str] = None

    # Armazenamento (S3 / Supabase Storage)
    S3_ENDPOINT: Optional[str] = None # Ex: https://[REF].supabase.co/storage/v1/s3
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_BUCKET: str = "manuscripto"
    S3_REGION: str = "sa-east-1"

    # Redis (Mensageria)
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    @model_validator(mode="after")
    def assemble_config(self) -> "Settings":
        """
        Interpola placeholders no DATABASE_URL e S3_ENDPOINT usando DATABASE_REF e DATABASE_PASSWORD.
        """
        if self.DATABASE_URL:
            if self.DATABASE_REF:
                self.DATABASE_URL = self.DATABASE_URL.replace("[REF-DO-PROJETO]", self.DATABASE_REF).replace("DATABASE_REF", self.DATABASE_REF)
            if self.DATABASE_PASSWORD:
                self.DATABASE_URL = self.DATABASE_URL.replace("[PASSWORD]", self.DATABASE_PASSWORD).replace("DATABASE_PASSWORD", self.DATABASE_PASSWORD)

        if self.DATABASE_REF:
            # Se o endpoint estiver ausente ou contiver os placeholders do exemplo
            placeholders = ["https://[REF].supabase.co", "https://DATABASE_REF.supabase.co"]
            if not self.S3_ENDPOINT or any(p in self.S3_ENDPOINT for p in placeholders):
                self.S3_ENDPOINT = f"https://{self.DATABASE_REF}.supabase.co/storage/v1/s3"
        return self

settings = Settings()