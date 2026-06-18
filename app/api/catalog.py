from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from app.db.session import get_db
from app import models, schemas

router = APIRouter()

@router.get("/vagas", response_model=List[schemas.VagaCatalog])
def list_active_vagas(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Lista as vagas de coautoria disponíveis no catálogo público.
    """
    return db.query(models.Vaga).options(
        joinedload(models.Vaga.publicacao).joinedload(models.Publicacao.criador)
    ).filter(
        models.Vaga.ativa == True,
        models.Vaga.quantidade_disponivel > 0
    ).offset(skip).limit(limit).all()

@router.get("/publicacoes", response_model=List[schemas.Publicacao])
def list_catalog_publications(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Lista publicações que possuem vagas de coautoria abertas.
    """
    return db.query(models.Publicacao).join(models.Vaga).filter(
        models.Vaga.ativa == True
    ).distinct().offset(skip).limit(limit).all()