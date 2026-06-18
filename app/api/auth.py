from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.services.cache_service import cache_service

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
    cache_key = f"user_profile:{user_id}"
    cached_user = cache_service.get(cache_key)
    if cached_user:
        try:
            return schemas.User.model_validate(cached_user) # Re-cria o modelo Pydantic a partir do dicionário em cache
        except Exception as e:
            # Loga o erro e prossegue para buscar do DB se os dados do cache estiverem malformados
            print(f"Erro ao validar dados de usuário em cache para {user_id}: {e}")

    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Converte o objeto SQLAlchemy para o modelo Pydantic
    user_pydantic = schemas.User.model_validate(user)
    cache_service.set(cache_key, user_pydantic.model_dump()) # Cacheia a representação em dicionário
    return user_pydantic # Retorna a instância do modelo Pydantic

@router.get("/profile/{user_id}/publications", response_model=List[schemas.Publicacao])
def get_user_publications(
    user_id: UUID,
    db: Session = Depends(get_db)
) -> Any:
    """Retorna as publicações em que o usuário especificado é autor/coautor."""
    cache_key = f"user_pubs:{user_id}"
    cached_pubs = cache_service.get(cache_key)
    if cached_pubs:
        try:
            return [schemas.Publicacao.model_validate(p) for p in cached_pubs] # Re-cria modelos Pydantic a partir da lista de dicionários em cache
        except Exception as e:
            # Loga o erro e prossegue para buscar do DB se os dados do cache estiverem malformados
            print(f"Erro ao validar dados de publicações em cache para {user_id}: {e}")

    pubs = db.query(models.Publicacao).join(models.AutorPublicacao).filter(
        models.AutorPublicacao.usuario_id == user_id
    ).all()
    
    # Converte a lista de publicações para modelos Pydantic
    pubs_pydantic = [schemas.Publicacao.model_validate(p) for p in pubs]
    cache_service.set(cache_key, [p.model_dump() for p in pubs_pydantic]) # Cacheia a lista de dicionários
    return pubs_pydantic # Retorna a lista de instâncias do modelo Pydantic

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
    
    # Invalida o cache para forçar a atualização na próxima leitura
    cache_service.invalidate_user_cache(current_user.id)
    return user