import redis
import json
from app.core.config import settings

class MessagingService:
    """
    Serviço para publicação de eventos em sistemas de mensageria (Redis).
    """
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST, 
            port=settings.REDIS_PORT, 
            decode_responses=True
        )

    def publicar_evento_compra(self, dados_compra: dict):
        """
        Envia os dados da compra para uma lista (fila) no Redis chamada 'eventos_compra'.
        """
        evento = json.dumps(dados_compra)
        self.redis_client.lpush("eventos_compra", evento)
        print(f"[MENSAGERIA] Evento de compra publicado: {dados_compra['compra_id']}")

messaging_service = MessagingService()