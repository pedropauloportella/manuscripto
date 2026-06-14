from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Importamos nossas configurações e a Base que centraliza os modelos
from app.core.config import settings
from app.db.base import Base

# Objeto de configuração do Alembic
config = context.config

# Configuração de logs baseada no alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Define o metadata para suporte a autogenerate
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Executa migrações em modo 'offline'."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "pyformat"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa migrações em modo 'online'."""
    # Utilizamos a URL definida no nosso Settings (.env)
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()