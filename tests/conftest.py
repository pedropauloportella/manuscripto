import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.core.config import settings
from fastapi.testclient import TestClient
import os

# 1. Prioridade para variável de env (CI)
# 2. Fallback para configuração no config.py
# 3. Fallback para o nome do serviço 'db' do docker-compose
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL_TEST") or \
                         settings.DATABASE_URL_TEST or \
                         "postgresql://postgres:postgres@db:5432/editora_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]