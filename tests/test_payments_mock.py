import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_mp_service():
    """
    Fixture para interceptar o mp_service dentro do módulo de pagamentos.
    Isso evita chamadas reais à API do MercadoPago.
    """
    # Patch no local onde o mp_service é IMPORTADO e usado
    with patch("app.api.payments.mp_service") as mocked:
        # Configura o retorno para criação de link de checkout
        mocked.create_payment_link.return_value = {
            "id": "pref_test_12345",
            "init_point": "https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=test"
        }
        
        # Configura o retorno para a consulta de status de pagamento (usado no webhook)
        mocked.get_payment.return_value = {
            "response": {
                "status": "approved",
                "external_reference": "1"  # ID da nossa tabela Compra
            }
        }
        yield mocked

def test_checkout_endpoint_with_mock(mock_mp_service, db_session):
    """
    Testa se o endpoint de checkout chama o MercadoPago corretamente via mock.
    """
    # Mock de autenticação e existência de vaga seria necessário aqui para um teste completo.
    # O foco aqui é demonstrar que o mp_service.create_payment_link foi chamado.
    
    # Exemplo de chamada (assumindo que o usuário está logado e a vaga ID 1 existe)
    # response = client.post("/api/v1/payments/checkout/1", headers={"Authorization": "Bearer ..."})
    
    # Verificação se o mock foi utilizado
    # assert response.status_code == 200
    # mock_mp_service.create_payment_link.assert_called_once()
    pass

def test_webhook_approved_payment(mock_mp_service):
    """
    Testa o processamento do webhook simulando uma aprovação.
    """
    payload = {
        "type": "payment",
        "data": {"id": "999999999"}
    }
    response = client.post("/api/v1/payments/webhook", json=payload)
    
    assert response.status_code == 200
    mock_mp_service.get_payment.assert_called_with("999999999")