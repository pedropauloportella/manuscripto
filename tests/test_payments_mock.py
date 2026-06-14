import pytest
from unittest.mock import patch
from app.main import app
from app import models

@pytest.fixture
def mock_mp_service():
    """
    Fixture para interceptar os serviços externos dentro do módulo de pagamentos.
    Isso evita chamadas reais à API do MercadoPago, Redis e E-mail.
    """
    with patch("app.api.payments.mp_service") as mocked_mp, \
         patch("app.api.payments.email_service") as mocked_email, \
         patch("app.api.payments.messaging_service") as mocked_msg:
        
        # Configura o retorno padrão para criação de link de checkout
        mocked_mp.create_payment_link.return_value = {
            "id": "pref_test_12345",
            "init_point": "https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=test"
        }
        
        # Configura o retorno padrão para a consulta de status de pagamento
        mocked_mp.get_payment.return_value = {
            "response": {
                "status": "approved",
                "external_reference": "00000000-0000-0000-0000-000000000001"
            }
        }
        
        yield mocked_mp

def test_checkout_endpoint_with_mock(mock_mp_service, db, client):
    """
    Testa se o endpoint de checkout chama o MercadoPago corretamente via mock.
    """
    # 1. Cria dados necessários no banco de teste
    user = models.Usuario(email="user@test.com", nome_completo="Test User", is_active=True)
    db.add(user)
    db.commit()
    
    pub = models.Publicacao(titulo="Livro Teste")
    db.add(pub)
    db.commit()
    
    vaga = models.Vaga(publicacao_id=pub.id, titulo="Vaga Teste", preco=100.0, quantidade_total=5, quantidade_disponivel=5)
    db.add(vaga)
    db.commit()

    # 2. Mock de autenticação (override do get_current_user)
    from app.api.deps import get_current_user
    app.dependency_overrides[get_current_user] = lambda: user

    # 3. Executa request de checkout
    response = client.post(f"/api/v1/payments/checkout/{vaga.id}")
    
    # 4. Asserts
    assert response.status_code == 200
    assert "init_point" in response.json()
    mock_mp_service.create_payment_link.assert_called_once()
    
    # Limpa override para não afetar outros testes
    del app.dependency_overrides[get_current_user]

def test_webhook_approved_payment(mock_mp_service, db, client):
    """
    Testa o processamento do webhook simulando uma aprovação.
    """
    # 1. Cria os registros necessários no banco para evitar o erro 404
    user = models.Usuario(email="autor@test.com", nome_completo="Autor Teste", is_active=True)
    db.add(user)
    db.commit()

    pub = models.Publicacao(titulo="Obra Cientifica")
    db.add(pub)
    db.commit()

    vaga = models.Vaga(publicacao_id=pub.id, titulo="Coautoria", preco=500.0, quantidade_total=2, quantidade_disponivel=2)
    db.add(vaga)
    db.commit()

    compra = models.Compra(usuario_id=user.id, vaga_id=vaga.id, valor_pago=500.0, status="pendente")
    db.add(compra)
    db.commit()
    db.refresh(compra)

    # 2. Ajusta o mock para retornar o ID real da compra criada no banco de teste
    mock_mp_service.get_payment.return_value = {
        "response": {
            "status": "approved",
            "external_reference": str(compra.id)
        }
    }

    # 3. Simula a chamada do Webhook do MercadoPago
    payload = {
        "type": "payment",
        "data": {"id": "999888777"}
    }
    response = client.post("/api/v1/payments/webhook", json=payload)
    
    # 4. Asserts
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    
    # Verifica se o banco de dados foi atualizado corretamente
    db.refresh(compra)
    assert compra.status == "aprovada"
    assert compra.id_pagamento_mp == "999888777"

    # Verifica se o vínculo de autor foi criado automaticamente
    vinculo = db.query(models.AutorPublicacao).filter(models.AutorPublicacao.compra_id == compra.id).first()
    assert vinculo is not None
    assert vinculo.usuario_id == user.id
    assert vinculo.funcao == "coautor"