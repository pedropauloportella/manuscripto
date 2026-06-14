import pytest
from unittest.mock import MagicMock
from app.db.session import get_db
from app.main import app
from fastapi.testclient import TestClient

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Pula a criação física do banco de dados para o CI/CD.
    Como o banco é externo (Supabase), os testes de integração de API
    utilizarão Mocks para a sessão do SQLAlchemy.
    """
    yield

@pytest.fixture
def db():
    """
    Retorna um Mock da sessão do banco de dados.
    Isso evita que os testes tentem conectar ao Postgres real.
    """
    mock_session = MagicMock()
    yield mock_session

@pytest.fixture
def client(db):
    """Injeta o mock do banco de dados no FastAPI durante os testes."""
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]