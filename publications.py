from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Publicacao, Vaga
from app import schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.Publicacao])
def list_publications(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return db.query(Publicacao).offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.Publicacao)
def create_publication(obj_in: schemas.PublicacaoCreate, db: Session = Depends(get_db)):
    db_obj = Publicacao(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/{pub_id}", response_model=schemas.Publicacao)
def get_publication(pub_id: int, db: Session = Depends(get_db)):
    pub = db.query(Publicacao).filter(Publicacao.id == pub_id).first()
    if not pub:
        raise HTTPException(status_code=404, detail="Publicação não encontrada")
    return pub

@router.post("/{pub_id}/vagas", response_model=schemas.Vaga)
def create_vaga(pub_id: int, obj_in: schemas.VagaCreate, db: Session = Depends(get_db)):
    # Verifica se a publicação existe
    pub = db.query(Publicacao).filter(Publicacao.id == pub_id).first()
    if not pub:
        raise HTTPException(status_code=404, detail="Publicação não encontrada")
    
    db_vaga = Vaga(**obj_in.dict(), publicacao_id=pub_id)
    db.add(db_vaga)
    db.commit()
    db.refresh(db_vaga)
    return db_vaga