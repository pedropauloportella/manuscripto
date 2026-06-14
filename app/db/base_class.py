import uuid
from sqlalchemy import Column, UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    # Classe base declarativa para todos os modelos do SQLAlchemy.
    # Como não usamos SQLite, usamos o UUID nativo do SQLAlchemy que mapeia para UUID no Postgres.
    # default=uuid.uuid4 garante a geração automática no servidor de aplicação.
    id = Column(UUID, primary_key=True, default=uuid.uuid4, index=True)
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()