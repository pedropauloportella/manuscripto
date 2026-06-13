from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import models, schemas
from app.api import deps
from app.services.storage import storage_service
from app.services.log_service import LogService

router = APIRouter()

@router.get("/", response_model=List[schemas.Publicacao])
def list_publications(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return db.query(models.Publicacao).offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.Publicacao)
def create_publication(obj_in: schemas.PublicacaoCreate, db: Session = Depends(get_db)):
    db_obj = models.Publicacao(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/{pub_id}", response_model=schemas.Publicacao)
def get_publication(pub_id: int, db: Session = Depends(get_db)):
    pub = db.query(models.Publicacao).filter(models.Publicacao.id == pub_id).first()
    if not pub:
        raise HTTPException(status_code=404, detail="Publicação não encontrada")
    return pub

@router.post("/{pub_id}/vagas", response_model=schemas.Vaga)
def create_vaga(pub_id: int, obj_in: schemas.VagaCreate, db: Session = Depends(get_db)):
    # Verifica se a publicação existe
    pub = db.query(models.Publicacao).filter(models.Publicacao.id == pub_id).first()
    if not pub:
        raise HTTPException(status_code=404, detail="Publicação não encontrada")
    
    db_vaga = models.Vaga(**obj_in.dict(), publicacao_id=pub_id, quantidade_disponivel=obj_in.quantidade_total)
    db.add(db_vaga)
    db.commit()
    db.refresh(db_vaga)
    return db_vaga

@router.post("/{pub_id}/versoes", response_model=schemas.Versao)
def upload_versao(
    pub_id: int,
    numero_versao: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(deps.get_current_user)
):
    # Verifica se o usuário tem permissão (é autor da publicação)
    autor_vinculo = db.query(models.AutorPublicacao).filter(
        models.AutorPublicacao.publicacao_id == pub_id,
        models.AutorPublicacao.usuario_id == current_user.id
    ).first()
    
    if not autor_vinculo and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Você não tem permissão para enviar versões desta obra")

    file_key = storage_service.upload_file(file)
    
    db_versao = models.Versao(
        publicacao_id=pub_id,
        numero_versao=numero_versao,
        caminho_arquivo_s3=file_key
    )
    db.add(db_versao)
    db.commit()
    db.refresh(db_versao)

    LogService.log_event(
        db=db,
        tipo_evento="upload",
        descricao=f"Nova versão {numero_versao} enviada para publicação {pub_id}",
        usuario_id=current_user.id,
        entidade_id=db_versao.id,
        entidade_tipo="Versao"
    )

    return db_versao

@router.get("/{pub_id}/versoes", response_model=List[schemas.Versao])
def list_versoes(
    pub_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(deps.get_current_user)
):
    """Lista todas as versões de uma publicação (Apenas para autores)."""
    autor_vinculo = db.query(models.AutorPublicacao).filter(
        models.AutorPublicacao.publicacao_id == pub_id,
        models.AutorPublicacao.usuario_id == current_user.id
    ).first()
    
    if not autor_vinculo and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Acesso negado")
        
    return db.query(models.Versao).filter(models.Versao.publicacao_id == pub_id).all()

@router.get("/{pub_id}/versoes/{versao_id}/download")
def download_versao(
    pub_id: int,
    versao_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(deps.get_current_user)
):
    """Gera link de download para uma versão específica."""
    autor_vinculo = db.query(models.AutorPublicacao).filter(
        models.AutorPublicacao.publicacao_id == pub_id,
        models.AutorPublicacao.usuario_id == current_user.id
    ).first()
    
    if not autor_vinculo and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Acesso negado")

    versao = db.query(models.Versao).filter(
        models.Versao.id == versao_id, 
        models.Versao.publicacao_id == pub_id
    ).first()
    
    if not versao:
        raise HTTPException(status_code=404, detail="Versão não encontrada")

    url = storage_service.get_presigned_url(versao.caminho_arquivo_s3)
    
    LogService.log_event(
        db=db,
        tipo_evento="download",
        descricao=f"Usuário {current_user.email} baixou a versão {versao.numero_versao} da publicação {pub_id}",
        usuario_id=current_user.id,
        entidade_id=versao.id,
        entidade_tipo="Versao"
    )
    
    return {"download_url": url}