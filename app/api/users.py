from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.services.seed_service import SeedService

router = APIRouter()

@router.get("/", response_model=List[schemas.User])
def list_users(
    db: Session = Depends(get_db),
    current_user: deps.UserFromJWT = Depends(deps.get_current_active_superuser),
    skip: int = 0,
    limit: int = 100
):
    """Lista todos os usuários (Apenas Superusers)."""
    users = db.query(models.Usuario).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=schemas.User)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: deps.UserFromJWT = Depends(deps.get_current_active_superuser)
):
    """Obtém detalhes de um usuário específico (Apenas Superusers)."""
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    user_id: UUID,
    user_in: schemas.UserAdminUpdate,
    db: Session = Depends(get_db),
    current_user: deps.UserFromJWT = Depends(deps.get_current_active_superuser)
):
    """Atualiza informações de um usuário (Apenas Superusers)."""
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    update_data = user_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(user, field, update_data[field])
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/seed-fictitious", status_code=201)
def seed_fictitious_data(
    db: Session = Depends(get_db),
    current_user: deps.UserFromJWT = Depends(deps.get_current_active_superuser)
):
    """Popula o banco de dados com usuários e publicações fictícios (Apenas Superusers)."""
    seed_service = SeedService(db)
    seed_service.seed_data(current_user.email, current_user.id)
    return {"message": "Dados fictícios criados com sucesso!"}

@router.delete("/clear-fictitious", status_code=204)
def clear_fictitious_data(
    db: Session = Depends(get_db),
    current_user: deps.UserFromJWT = Depends(deps.get_current_active_superuser)
):
    """Remove todos os dados fictícios do banco de dados (Apenas Superusers)."""
    # Previne que o superuser logado seja deletado se ele não for recriado no seed
    # Para este cenário, o seed_data recria o admin, então podemos deletar tudo.
    seed_service = SeedService(db)
    seed_service.clear_data()
    return None

@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: deps.UserFromJWT = Depends(deps.get_current_active_superuser)
):
    """Remove um usuário (Apenas Superusers)."""
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db.delete(user)
    db.commit()
    return None

@router.put("/{user_id}/toggle-superuser", response_model=schemas.User)
def toggle_superuser_status(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: deps.UserFromJWT = Depends(deps.get_current_active_superuser)
):
    """Alterna o status de superuser de um usuário (Apenas Superusers)."""
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Previne que um superuser remova seus próprios privilégios acidentalmente
    if user.id == current_user.id and user.is_superuser:
        # Verifica se há pelo menos um outro superuser ativo
        other_superusers = db.query(models.Usuario).filter(
            models.Usuario.is_superuser == True,
            models.Usuario.id != user_id
        ).count()
        if other_superusers == 0:
            raise HTTPException(
                status_code=400,
                detail="Não é possível remover o único superuser do sistema."
            )

    user.is_superuser = not user.is_superuser
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.put("/{user_id}/toggle-active", response_model=schemas.User)
def toggle_active_status(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: deps.UserFromJWT = Depends(deps.get_current_active_superuser)
):
    """Alterna o status de ativo de um usuário (Apenas Superusers)."""
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Previne que um superuser se desative acidentalmente
    if user.id == current_user.id and user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Um superuser não pode desativar sua própria conta."
        )

    user.is_active = not user.is_active
    db.add(user)
    db.commit()
    db.refresh(user)
    return user