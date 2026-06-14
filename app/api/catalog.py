from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import models, schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.Publicacao])
def get_public_catalog(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Lista todas as publicações que possuem pelo menos uma vaga ativa no momento.
    """
    return db.query(models.Publicacao).join(models.Vaga).filter(
        models.Vaga.ativa == True,
        models.Vaga.quantidade_disponivel > 0
    ).distinct().offset(skip).limit(limit).all()

@router.get("/{pub_id}/vagas", response_model=List[schemas.Vaga])
def get_publication_vagas(pub_id: UUID, db: Session = Depends(get_db)):
    """
    Lista as vagas disponíveis para uma publicação específica selecionada no catálogo.
    """
    vagas = db.query(models.Vaga).filter(
        models.Vaga.publicacao_id == pub_id,
        models.Vaga.ativa == True,
        models.Vaga.quantidade_disponivel > 0
    ).all()
    
    return vagas