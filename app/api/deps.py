from typing import Generator, Optional, Any
from fastapi import Depends, HTTPException, status
from uuid import UUID
from fastapi.security import OAuth2PasswordBearer # Mantemos para extrair o token do header
from jose import jwt, JWTError
from pydantic import BaseModel, ValidationError # Importamos BaseModel para criar o UserFromJWT
import httpx

from app.core.config import settings
# Não precisamos mais de 'db' ou 'models' para get_current_user
# from app.db.session import get_db
# from app import models, schemas

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login" # tokenUrl é para documentação OpenAPI
)

# Define um esquema de usuário que pode ser construído diretamente a partir dos claims do JWT.
# Este esquema reflete as informações essenciais do usuário para autorização.
class UserFromJWT(BaseModel):
    id: UUID
    email: str
    is_active: bool = True
    is_superuser: bool = False # Corresponde ao 'is_admin' do Supabase app_metadata
    nome_completo: Optional[str] = None
    orcid_id: Optional[str] = None

# Cache simples para as chaves do Supabase para não sobrecarregar a rede
_jwks_cache: Optional[dict] = None

async def get_supabase_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        if not settings.DATABASE_REF:
            raise ValueError("DATABASE_REF não configurado no .env")
        url = f"https://{settings.DATABASE_REF}.supabase.co/auth/v1/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            _jwks_cache = response.json()
    return _jwks_cache

async def get_current_user(
    token: str = Depends(reusable_oauth2)
) -> UserFromJWT:
    """
    Valida o token JWT e recupera o usuário atual dos claims do token.
    """
    try:
        # 1. Identifica o algoritmo e a chave no header do token
        unverified_header = jwt.get_unverified_header(token)
        algorithm = unverified_header.get("alg")
        
        # 2. Se for HS256, usa o segredo do .env. Se for ES256, busca no JWKS.
        if algorithm == "HS256":
            key = settings.SUPABASE_JWT_SECRET or settings.SECRET_KEY
        else:
            # Busca as chaves públicas do Supabase (contém a chave para ES256)
            jwks = await get_supabase_jwks()
            # O python-jose consegue validar usando o objeto JWKS completo 
            # se passarmos a chave correta baseada no 'kid' (Key ID)
            key = jwks

        # 3. Decodifica o token
        payload = jwt.decode(
            token,
            key,
            algorithms=["HS256", "ES256"],
            audience="authenticated",
            options={"verify_aud": False}
        )
        
        user_id = UUID(payload.get("sub"))
        user_email = payload.get("email")
        
        # O Supabase coloca claims customizados dentro do objeto 'app_metadata' no JWT
        # Verificamos no app_metadata e também na raiz, para maior compatibilidade
        app_metadata = payload.get("app_metadata", {})
        is_admin = app_metadata.get("is_admin", payload.get("is_admin", False))
        
        # Extrai metadados do perfil (nome, etc) vindos do Google/ORCID/Cadastro
        user_metadata = payload.get("user_metadata", {})
        
        # Cria um objeto UserFromJWT diretamente a partir dos claims
        user = UserFromJWT(
            id=user_id,
            email=user_email,
            is_active=True, # Assumimos que o usuário está ativo se o token é válido
            is_superuser=is_admin,
            nome_completo=user_metadata.get("full_name") or user_metadata.get("nome_completo"),
            orcid_id=user_metadata.get("orcid")
        )
        return user
    except Exception as e:
        # Capturamos qualquer erro (assinatura, PEM malformado, alg inválido) para evitar 500 Internal Server Error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Falha na autenticação: {str(e)}",
        )

def get_current_active_superuser(
    current_user: UserFromJWT = Depends(get_current_user),
) -> UserFromJWT:
    """
    Verifica se o usuário atual tem permissões de administrador.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="O usuário não tem privilégios suficientes")
    return current_user