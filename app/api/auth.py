from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.db.session import get_db

router = APIRouter()

@router.get("/me/publications", response_model=List[schemas.Publicacao])
def read_user_publications(
    current_user: deps.UserFromJWT = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Retorna as publicações em que o usuário logado é autor/coautor."""
    # Consulta a tabela de vínculo diretamente usando o UUID do token
    return db.query(models.Publicacao).join(models.AutorPublicacao).filter(
        models.AutorPublicacao.usuario_id == current_user.id
    ).all()

@router.get("/me", response_model=deps.UserFromJWT)
def read_user_me(
    current_user: deps.UserFromJWT = Depends(deps.get_current_user)
) -> Any:
    """Retorna o perfil do usuário logado."""
    return current_user