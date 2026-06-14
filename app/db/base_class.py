import uuid
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    # Classe base declarativa para todos os modelos do SQLAlchemy.
    # Fornece id como UUID e geração automática do nome da tabela.
    # default=uuid.uuid4 garante um UUID caso o provedor (ORCID/Supabase) não envie um.
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()