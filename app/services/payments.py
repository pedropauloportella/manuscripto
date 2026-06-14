from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from app.services.mercadopago_service import mp_service

router = APIRouter()

@router.post("/checkout/{publication_id}")
async def create_checkout(publication_id: int, user_id: int, db: Session = Depends(get_db)):
    pub = db.query(models.Publication).filter(models.Publication.id == publication_id).first()
    if not pub or not pub.is_open_vacancy:
        raise HTTPException(status_code=404, detail="Vaga não disponível")

    # 1. Registra intenção de pagamento no banco
    db_payment = models.Payment(user_id=user_id, publication_id=publication_id, status="pending")
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    # 2. Gera link no MercadoPago
    mp_preference = mp_service.create_payment_link(pub.title, pub.price, db_payment.id)
    
    db_payment.mp_preference_id = mp_preference["id"]
    db.commit()

    return {"init_point": mp_preference["init_point"]}

@router.post("/webhook")
async def mp_webhook(request: Request, db: Session = Depends(get_db)):
    # Simplificado para o MVP: O MercadoPago envia notificações de atualização
    # Aqui você verificaria o status real via API do MP usando o ID recebido
    data = await request.json()
    
    if data.get("action") == "payment.created": # Exemplo de trigger
        # Lógica para:
        # 1. Localizar o Payment via external_reference
        # 2. Atualizar status para 'approved'
        # 3. Adicionar o user_id na lista de authors da Publication (tabela associativa)
        pass
        
    return {"status": "ok"}