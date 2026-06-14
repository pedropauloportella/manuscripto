import redis
import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import models, schemas
from app.api import deps
from app.core.config import settings

router = APIRouter()
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)

@router.post("/checkout/{vaga_id}")
def create_checkout(
    vaga_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(deps.get_current_user)
):
    vaga = db.query(models.Vaga).filter(models.Vaga.id == vaga_id).first()
    if not vaga or not vaga.ativa or vaga.quantidade_disponivel <= 0:
        raise HTTPException(status_code=400, detail="Vaga indisponível")

    # Simulação de criação de preferência MP
    return {
        "init_point": "https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=simulated",
        "preference_id": "simulated_id",
        "external_reference": str(vaga.id)
    }

@router.post("/webhook")
async def mercadopago_webhook(request: Request):
    """Recebe a notificação do MercadoPago e dispara evento para o Worker."""
    payload = await request.json()
    
    # Publica no Redis para o worker processar a vinculação do coautor
    event_data = {
        "type": "payment.success",
        "vaga_id": payload.get("external_reference"),
        "data": payload
    }
    redis_client.publish("eventos_compra", json.dumps(event_data))
    
    return {"status": "ok"}