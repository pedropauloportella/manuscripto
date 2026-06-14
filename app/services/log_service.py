from sqlalchemy.orm import Session
from app import models
from typing import Optional

class LogService:
    @staticmethod
    def log_event(
        db: Session,
        tipo_evento: str,
        descricao: str,
        usuario_id: Optional[int] = None,
        entidade_id: Optional[int] = None,
        entidade_tipo: Optional[str] = None
    ):
        db_log = models.LogEvento(
            tipo_evento=tipo_evento,
            descricao=descricao,
            usuario_id=usuario_id,
            entidade_id=entidade_id,
            entidade_tipo=entidade_tipo
        )
        db.add(db_log)
        db.commit()
        return db_log