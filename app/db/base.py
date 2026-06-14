# Importe todos os modelos aqui para que o Alembic possa detectá-los
from app.db.base_class import Base  # noqa
from app.models import Usuario, Publicacao, Vaga, Compra, AutorPublicacao, Versao, LogEvento  # noqa