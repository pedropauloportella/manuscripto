import redis
import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import models, schemas
from app.api import deps
from app.core.config import settings
from app.services.mercadopago_service import mp_service
# Importe os serviços reais quando estiverem implementados em seus respectivos arquivos
# from app.services.email_service import email_service 
# from app.services.messaging_service import messaging_service

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
    # Nota: Ajustado para usar os parâmetros esperados pelo MercadoPagoService real
    preference = mp_service.create_payment_link(vaga.titulo, float(vaga.preco), str(compra.id))
    
    return {
        "init_point": preference["init_point"],
        "preference_id": preference["id"],
        "external_reference": str(compra.id)
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
                # Aqui você chamaria os serviços reais importados
                # email_service.send_confirmation(compra.usuario.email, compra.vaga.publicacao.titulo)
                redis_client.publish("eventos_compra", json.dumps({"compra_id": str(compra.id), "status": "approved"}))
                
                db.commit()

    return {"status": "ok"}