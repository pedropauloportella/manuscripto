import uuid
from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    # Classe base declarativa para todos os modelos do SQLAlchemy.
    # Usamos o UUID do dialeto PostgreSQL para garantir que o Alembic gere 'UUID' e não 'INTEGER'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"), index=True)
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()