from typing import Any
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    # Classe base declarativa para todos os modelos do SQLAlchemy.
    # Fornece id e geração automática do nome da tabela.
    id = Column(Integer, primary_key=True, index=True)
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()