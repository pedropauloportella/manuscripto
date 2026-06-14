# Importa a Base e todos os modelos para que o SQLAlchemy/Alembic os reconheça
from app.db.base_class import Base
from app.models import Usuario, Publicacao, Vaga, Compra, AutorPublicacao, Versao, LogEvento