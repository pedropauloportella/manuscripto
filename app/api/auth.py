from datetime import timedelta
from typing import Any, List
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

@router.get("/me/publications", response_model=List[schemas.Publicacao])
def read_user_publications(
    current_user: models.Usuario = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Retorna as publicações em que o usuário logado é autor/coautor."""
    return [
        vinculo.publicacao 
        for vinculo in current_user.publicacoes
    ]

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
                "redirect_uri": f"http://localhost:8000{settings.API_V1_STR}/auth/orcid/callback",
                "code": code,
            },
            headers={"Accept": "application/json"}
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Falha na autenticação com ORCID")

    data = response.json()
    orcid_id = data.get("orcid")
    nome = data.get("name")

    # Busca ou Cria o usuário
    user = db.query(models.Usuario).filter(models.Usuario.orcid_id == orcid_id).first()

    if not user:
        # Como o ORCID as vezes não retorna email público no token inicial, 
        # usamos o orcid_id como identificador único ou placeholder
        user = models.Usuario(
            orcid_id=orcid_id,
            nome_completo=nome,
            email=f"{orcid_id}@orcid.org", # Placeholder se email não disponível
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": utils.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """Troca o código do Google por um token e loga o usuário."""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Configuração do Google OAuth ausente")

    async with httpx.AsyncClient() as client:
        # 1. Trocar o código pelo token de acesso
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": f"http://localhost:8000{settings.API_V1_STR}/auth/google/callback",
            },
        )

        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Falha na autenticação com Google (token)")

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        # 2. Obter informações do perfil do usuário
        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if user_info_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Falha ao obter dados do usuário no Google")

        user_data = user_info_response.json()
        email = user_data.get("email")
        nome = user_data.get("name")

    if not email:
        raise HTTPException(status_code=400, detail="Email não retornado pelo Google")

    # 3. Busca ou Cria o usuário no banco local
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()

    if not user:
        user = models.Usuario(
            email=email,
            nome_completo=nome,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 4. Gerar o token de acesso (JWT) do Manuscripto
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": utils.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }