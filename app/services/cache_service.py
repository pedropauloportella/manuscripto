import json
import redis
from typing import Optional, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class CacheService:
    _redis_client: Optional[redis.Redis] = None

    @property
    def redis_client(self) -> Optional[redis.Redis]:
        if self._redis_client is None:
            try:
                # Adicionamos um timeout de 1 segundo para evitar que a app trave se o Redis cair
                self._redis_client = redis.from_url(
                    settings.REDIS_URL, 
                    decode_responses=True,
                    socket_connect_timeout=1
                )
                self._redis_client.ping() # Testa a conexão
                logger.info("Successfully connected to Redis.")
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
                logger.error(f"Could not connect to Redis: {e}. Caching will be disabled.")
                self._redis_client = None # Garante que seja None se a conexão falhar
        return self._redis_client

    def get(self, key: str) -> Optional[Any]:
        """Recupera um valor do cache e o desserializa."""
        client = self.redis_client
        if client:
            try:
                data = client.get(key)
                if data:
                    return json.loads(data)
            except redis.exceptions.ConnectionError as e:
                logger.error(f"Redis connection error during GET for key {key}: {e}")
                self._redis_client = None # Força a reconexão na próxima tentativa
        return None

    def set(self, key: str, value: Any, expire: int = 3600):
        """Armazena um valor no cache serializado como JSON."""
        client = self.redis_client
        if client:
            try:
                client.set(
                    key,
                    json.dumps(value, default=str), # default=str lida com UUIDs e Datas
                    ex=expire
                )
            except redis.exceptions.ConnectionError as e:
                logger.error(f"Redis connection error during SET for key {key}: {e}")
                self._redis_client = None # Força a reconexão na próxima tentativa

    def delete(self, key: str):
        """Remove uma chave específica do cache."""
        client = self.redis_client
        if client:
            try:
                client.delete(key)
            except redis.exceptions.ConnectionError as e:
                logger.error(f"Redis connection error during DELETE for key {key}: {e}")
                self._redis_client = None # Força a reconexão na próxima tentativa

    def invalidate_user_cache(self, user_id: Any):
        """Atalho para invalidar todos os caches relacionados a um usuário."""
        self.delete(f"user_profile:{user_id}")
        self.delete(f"user_pubs:{user_id}")

    def flush_all(self):
        """Limpa todo o banco de dados do Redis."""
        client = self.redis_client
        if client:
            try:
                client.flushdb()
            except redis.exceptions.ConnectionError as e:
                logger.error(f"Redis connection error during FLUSH_ALL: {e}")
                self._redis_client = None # Força a reconexão na próxima tentativa

cache_service = CacheService()