# app/db/base_class.py
# Propósito: Define a classe base declarativa para os modelos SQLAlchemy,
# incluindo um campo 'id' comum a todas as tabelas.
# Variáveis de ambiente importantes: Nenhuma.

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer
from sqlalchemy.orm import declared_attr

Base = declarative_base()

class CustomBase(Base):
    """
    Classe base personalizada para todos os modelos SQLAlchemy.
    Adiciona um campo `id` de chave primária auto-incrementável.
    """
    __abstract__ = True  # Indica que esta classe é abstrata e não deve ser mapeada para uma tabela.

    # Adiciona a coluna 'id' como chave primária auto-incrementável.
    # @declared_attr permite que esta coluna seja definida uma vez na base
    # e adicionada a cada subclasse que herdar dela.
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Para evitar conflitos de nomes se a classe base Declarative do SQLAlchemy
    # for usada diretamente em outros lugares, podemos usar esta classe CustomBase
    # como a verdadeira base para nossos modelos.
```
<!--
[PROMPT_SUGGESTION]Refactor `app/db/base.py` to use `CustomBase` instead of `Base` from `sqlalchemy.ext.declarative` for consistency.[/PROMPT_SUGGESTION]
[PROMPT_SUGGESTION]Implement the endpoints for CRUD operations on Publicacao and Vaga in `app/api/publications.py` and `app/api/vagas.py` respectively, including request/response schemas.[/PROMPT_SUGGESTION]
->
