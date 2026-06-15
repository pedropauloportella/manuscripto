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

# --- Serviços de Suporte (Placeholders para o Service Layer) ---
class MercadoPagoService:
    def create_payment_link(self, vaga: models.Vaga, user_id: UUID):
        # Aqui viria a integração real com o SDK do MercadoPago
        return {
            "init_point": "https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=simulated",
            "id": "simulated_id"
        }
    
    def get_payment(self, payment_id: str):
        # Simulação de consulta à API do MP para validar o status
        return {
            "response": {
                "status": "approved",
                "external_reference": "uuid-da-compra-aqui"
            }
        }

class EmailService:
    def send_confirmation(self, email: str, pub_titulo: str):
        pass

class MessagingService:
    def publish_purchase_event(self, event_data: dict):
        redis_client.publish("eventos_compra", json.dumps(event_data))

# Instâncias globais para permitir o mock nos testes
mp_service = MercadoPagoService()
email_service = EmailService()
messaging_service = MessagingService()

@router.post("/checkout/{vaga_id}")
def create_checkout(
    vaga_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(deps.get_current_user)
):
    vaga = db.query(models.Vaga).filter(models.Vaga.id == vaga_id).first()
    if not vaga or not vaga.ativa or vaga.quantidade_disponivel <= 0:
        raise HTTPException(status_code=400, detail="Vaga indisponível")

    # 1. Cria o registro da compra no banco (pendente)
    compra = models.Compra(
        usuario_id=current_user.id,
        vaga_id=vaga.id,
        valor_pago=vaga.preco,
        status="pendente"
    )
    db.add(compra)
    db.commit()
    db.refresh(compra)

    # 2. Gera a preferência no MercadoPago via serviço
    preference = mp_service.create_payment_link(vaga, current_user.id)
    
    return {
        "init_point": preference["init_point"],
        "preference_id": preference["id"],
        "external_reference": str(compra.id) # Vinculamos o ID da nossa Compra à ref do MP
    }

@router.post("/webhook")
async def mercadopago_webhook(request: Request, db: Session = Depends(get_db)):
    """Recebe a notificação do MercadoPago e processa a aprovação."""
    payload = await request.json()
    
    # Conforme o teste test_webhook_approved_payment, processamos o status "approved"
    if payload.get("type") == "payment":
        payment_id = payload["data"]["id"]
        payment_info = mp_service.get_payment(payment_id)
        
        if payment_info["response"]["status"] == "approved":
            compra_id = payment_info["response"]["external_reference"]
            compra = db.query(models.Compra).filter(models.Compra.id == compra_id).first()
            
            if compra and compra.status != "aprovada":
                # 1. Atualiza status da compra
                compra.status = "aprovada"
                compra.id_pagamento_mp = payment_id
                
                # 2. Cria o vínculo de coautor (objetivo do MVP)
                vinculo = models.AutorPublicacao(
                    usuario_id=compra.usuario_id,
                    publicacao_id=compra.vaga.publicacao_id,
                    funcao="coautor"
                )
                db.add(vinculo)
                
                # 3. Notificações e Side-effects
                email_service.send_confirmation(compra.usuario.email, compra.vaga.publicacao.titulo)
                messaging_service.publish_purchase_event({"compra_id": str(compra.id), "status": "approved"})
                
                db.commit()

    return {"status": "ok"}