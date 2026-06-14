from sqlalchemy.orm import Session
from app import models

class LogService:
    @staticmethod
    def log_event(
        db: Session,
        tipo_evento: str,
        descricao: str,
        usuario_id: int = None,
        entidade_id: int = None,
        entidade_tipo: str = None
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