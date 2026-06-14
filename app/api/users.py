from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.Usuario = Depends(deps.get_current_active_superuser),
):
    """
    Lista todos os usuários cadastrados. (Apenas Administradores)
    """
    users = db.query(models.Usuario).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_superuser),
):
    """
    Busca um usuário específico pelo ID. (Apenas Administradores)
    """
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    user_id: UUID,
    obj_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_superuser),
):
    """
    Atualiza os dados de um usuário (Ativar/Desativar, Promover a Admin). (Apenas Administradores)
    """
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    update_data = obj_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(user, field, update_data[field])
    
    db.commit()
    db.refresh(user)
    return user