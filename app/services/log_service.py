import uuid
from sqlalchemy.orm import Session
from app import models

class LogService:
    """
    Serviço centralizado para persistência de logs de eventos do sistema.
    """
    @staticmethod
    def log_event(
        db: Session,
        tipo_evento: str,
        descricao: str,
        usuario_id: uuid.UUID = None,
        entidade_id: uuid.UUID = None,
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
        # O commit é feito aqui para garantir que o log seja salvo independente
        # do sucesso da transação principal em alguns fluxos de erro.
        db.commit()