import mercadopago
from typing import Union
from app.core.config import settings

class MercadoPagoService:
    def __init__(self):
        # O SDK do MercadoPago exige que o access_token seja uma string.
        # Em ambientes de teste ou CI onde a variável não está definida,
        # passamos uma string vazia para evitar erro na inicialização do módulo.
        token = settings.MERCADOPAGO_ACCESS_TOKEN or ""
        self.sdk = mercadopago.SDK(token)

    def create_payment_link(self, title: str, price: float, payment_id: Union[str, int]):
        """
        Cria um link de pagamento. 
        O 'external_reference' vincula o ID do nosso banco ao MercadoPago.
        """
        preference_data = {
            "items": [
                {
                    "title": title,
                    "quantity": 1,
                    "unit_price": price,
                    "currency_id": "BRL"
                }
            ],
            "external_reference": str(payment_id),
            "notification_url": f"{settings.API_BASE_URL}{settings.API_V1_STR}/payments/webhook",
        }
        preference_response = self.sdk.preference().create(preference_data)
        return preference_response["response"]

    def get_payment(self, payment_id: str):
        """
        Busca informações de um pagamento específico.
        """
        return self.sdk.payment().get(payment_id)

mp_service = MercadoPagoService()