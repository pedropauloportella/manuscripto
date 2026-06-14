import mercadopago
from app.core.config import settings

class MercadoPagoService:
    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    def create_payment_link(self, title: str, price: float, payment_id: int):
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

mp_service = MercadoPagoService()