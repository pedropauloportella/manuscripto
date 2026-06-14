from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app import models

class LogService:
    @staticmethod
    def log_event(
        db: Session,
        tipo_evento: str,
        descricao: str,
        usuario_id: Optional[UUID] = None,
        entidade_id: Optional[UUID] = None,
        entidade_tipo: Optional[str] = None
    ):
        """Registra um evento de auditoria no banco de dados."""
        db_log = models.LogEvento(
            tipo_evento=tipo_evento,
            descricao=descricao,
            usuario_id=usuario_id,
            entidade_id=entidade_id,
            entidade_tipo=entidade_tipo
        )
        db.add(db_log)
        db.commit()