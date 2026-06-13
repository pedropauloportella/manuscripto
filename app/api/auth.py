from datetime import timedelta
from typing import Any
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.auth import utils
from app.core.config import settings

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """Login via formulário padrão (Email/Senha)."""
    user = db.query(models.Usuario).filter(models.Usuario.email == form_data.username).first()
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Email ou senha incorretos")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": utils.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.Usuario = Depends(deps.get_current_user),
) -> Any:
    """Retorna o perfil do usuário logado."""
    return current_user

@router.get("/orcid/callback")
async def orcid_callback(code: str, db: Session = Depends(get_db)):
    """Troca o código do ORCID por um token e loga o usuário."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://orcid.org/oauth/token",
            data={
                "client_id": settings.ORCID_CLIENT_ID,
                "client_secret": settings.ORCID_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
            },
            headers={"Accept": "application/json"}
        )
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Falha na autenticação com ORCID")
    
    data = response.json()
    # Aqui você buscaria o usuário pelo data['orcid'] ou criaria um novo
    # e então geraria o token JWT do sistema usando utils.create_access_token
    
    return {
        "orcid": data.get("orcid"),
        "name": data.get("name"),
        "msg": "Integração parcial: Implementar persistência de usuário."
    }