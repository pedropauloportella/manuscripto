from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Verifica se o endpoint raiz retorna a mensagem de boas-vindas."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Bem-vindo à API do Manuscripto"
    assert data["docs"] == "/docs"
    assert "data_atual" in data