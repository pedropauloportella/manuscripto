from typing import Any
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """Classe base para todos os modelos SQLAlchemy, provendo o campo 'id'."""
    id: Mapped[int] = mapped_column(primary_key=True, index=True)