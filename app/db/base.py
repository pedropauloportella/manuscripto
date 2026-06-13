# Propósito: Centralizar a base declarativa para os modelos SQLAlchemy e importar todos os modelos
# para que o Alembic os detecte automaticamente.

from app.db.base_class import Base  # noqa: F401 - Importa a Base declarativa personalizada
# Importar todos os modelos aqui para que o Alembic os detecte
from app.models import Usuario, Publicacao, Vaga, Compra, AutorPublicacao, Versao, LogEvento, Base # noqa: F401
