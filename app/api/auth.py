from typing import Any, List
from uuid import UUID
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

@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: deps.UserFromJWT = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Retorna o perfil do usuário logado."""
    user = db.query(models.Usuario).filter(models.Usuario.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.get("/profile/{user_id}", response_model=schemas.User)
def get_public_profile(
    user_id: UUID,
    db: Session = Depends(get_db)
) -> Any:
    """Retorna os dados públicos de um perfil através do ID."""
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.put("/me", response_model=schemas.User)
def update_user_me(
    obj_in: schemas.UserUpdate,
    current_user: deps.UserFromJWT = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Atualiza o perfil do usuário logado."""
    user = db.query(models.Usuario).filter(models.Usuario.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    update_data = obj_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(user, field, update_data[field])
    
    db.commit()
    db.refresh(user)
    return user