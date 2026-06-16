from typing import Generator
from fastapi import Depends, HTTPException, status
from uuid import UUID
from fastapi.security import OAuth2PasswordBearer # Mantemos para extrair o token do header
from jose import jwt, JWTError
from pydantic import BaseModel, ValidationError # Importamos BaseModel para criar o UserFromJWT

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

def get_current_user(
    token: str = Depends(reusable_oauth2)
) -> UserFromJWT:
    """
    Valida o token JWT e recupera o usuário atual dos claims do token.
    Não consulta o banco de dados local para informações do usuário.
    """
    # Supabase usa algoritmo HS256 por padrão
    jwt_secret = settings.SUPABASE_JWT_SECRET or settings.SECRET_KEY
    try:
        # Obtemos o cabeçalho para identificar o algoritmo e evitar o erro "alg value not allowed"
        unverified_header = jwt.get_unverified_header(token)
        algorithm = unverified_header.get("alg", "HS256")

        # Decodificamos o token. O 'verify_aud' é desabilitado para maior compatibilidade em dev.
        payload = jwt.decode(
            token, jwt_secret, algorithms=[algorithm], options={"verify_aud": False}
        )
        
        user_id = UUID(payload.get("sub"))
        user_email = payload.get("email")
        
        # O Supabase coloca claims customizados dentro do objeto 'app_metadata' no JWT
        # Verificamos no app_metadata e também na raiz, para maior compatibilidade
        app_metadata = payload.get("app_metadata", {})
        is_admin = app_metadata.get("is_admin", payload.get("is_admin", False))
        
        # Cria um objeto UserFromJWT diretamente a partir dos claims
        user = UserFromJWT(
            id=user_id,
            email=user_email,
            is_active=True, # Assumimos que o usuário está ativo se o token é válido
            is_superuser=is_admin # Define is_superuser com base no claim 'is_admin'
        )
        return user
    except (JWTError, ValidationError, ValueError) as e: # Adicionado ValueError para conversão de UUID
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido ou expirado: {e}",
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