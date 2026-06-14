from typing import Generator
from fastapi import Depends, HTTPException, status
from uuid import UUID
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.db.session import get_db
from app.core.config import settings
from app import models, schemas

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login" # Opcional se usar Supabase Auth no Front
)

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.Usuario:
    """
    Valida o token JWT e recupera o usuário atual do banco de dados.
    """
    # Supabase usa algoritmo HS256 por padrão
    jwt_secret = settings.SUPABASE_JWT_SECRET or settings.SECRET_KEY
    try:
        payload = jwt.decode(
            token, jwt_secret, algorithms=["HS256"], audience="authenticated"
        )
        token_data = schemas.TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não foi possível validar as credenciais",
        )
    user = db.query(models.Usuario).filter(models.Usuario.id == UUID(token_data.sub)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return user

def get_current_active_superuser(
    current_user: models.Usuario = Depends(get_current_user),
) -> models.Usuario:
    """
    Verifica se o usuário atual tem permissões de administrador.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="O usuário não tem privilégios suficientes")
    return current_user