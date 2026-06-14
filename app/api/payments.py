from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import models, schemas
from app.api import deps
from app.services.mercadopago_service import mp_service
from app.services.log_service import LogService
from app.services.email_service import email_service
from app.services.messaging_service import messaging_service

router = APIRouter()

@router.post("/checkout/{vaga_id}")
async def create_checkout(
    vaga_id: UUID, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(deps.get_current_user)
):
    # Busca a vaga específica
    vaga = db.query(models.Vaga).filter(models.Vaga.id == vaga_id, models.Vaga.ativa == True).first()
    if not vaga or vaga.quantidade_disponivel <= 0:
        raise HTTPException(status_code=404, detail="Vaga não disponível")

    # 1. Registra intenção de pagamento
    db_payment = models.Compra(
        usuario_id=current_user.id, 
        vaga_id=vaga.id, 
        valor_pago=vaga.preco,
        status="pendente"
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    # 2. Gera link no MercadoPago
    mp_preference = mp_service.create_payment_link(vaga.titulo, float(vaga.preco), db_payment.id)
    
    db_payment.mp_preference_id = mp_preference["id"]
    db.commit()

    LogService.log_event(
        db=db,
        tipo_evento="checkout_iniciado",
        descricao=f"Usuário {current_user.id} iniciou checkout para vaga {vaga_id}",
        usuario_id=current_user.id,
        entidade_id=db_payment.id,
        entidade_tipo="Compra"
    )

    return {"init_point": mp_preference["init_point"]}

@router.post("/webhook")
async def mp_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    payment_id = data.get("data", {}).get("id") or request.query_params.get("data.id")
    
    if data.get("type") == "payment" and payment_id:
        payment_info = mp_service.get_payment(str(payment_id))
        payment_status = payment_info["response"]["status"]
        external_ref = payment_info["response"]["external_reference"]

        try:
            compra_id = UUID(external_ref)
        except (ValueError, TypeError):
            # Caso o external_ref não seja um UUID válido (pode ocorrer em logs antigos)
            raise HTTPException(status_code=400, detail="ID de referência inválido")

        db_payment = db.query(models.Compra).filter(models.Compra.id == compra_id).first()
        
        if not db_payment:
            raise HTTPException(status_code=404, detail="Compra não encontrada")

        if payment_status == "approved":
            if db_payment.status != "aprovada":
                db_payment.status = "aprovada"
                db_payment.id_pagamento_mp = str(payment_id)
                
                vaga = db.query(models.Vaga).filter(models.Vaga.id == db_payment.vaga_id).first()
                
                # Verificação de segurança: garante que a vaga ainda está disponível
                # no momento da confirmação do pagamento.
                if vaga and vaga.quantidade_disponivel > 0:
                    novo_autor = models.AutorPublicacao(
                        usuario_id=db_payment.usuario_id,
                        publicacao_id=vaga.publicacao_id,
                        compra_id=db_payment.id,
                        funcao="coautor"
                    )
                    db.add(novo_autor)
                    vaga.quantidade_disponivel -= 1
                
                    # Notificações e Eventos só ocorrem se o vínculo foi criado
                    email_service.enviar_confirmacao_coautoria(
                        email_destino=db_payment.usuario.email,
                        nome_usuario=db_payment.usuario.nome_completo,
                        titulo_obra=vaga.publicacao.titulo if vaga and vaga.publicacao else "Obra"
                    )
                else:
                    # Caso a vaga tenha acabado entre o checkout e o webhook (overselling)
                    # Aqui deveríamos disparar um alerta para estorno manual ou suporte.
                    LogService.log_event(
                        db=db,
                        tipo_evento="erro_vagas_esgotadas",
                        descricao=f"Pagamento aprovado para Compra {db_payment.id}, mas vagas esgotadas.",
                        usuario_id=db_payment.usuario_id
                    )
                
                # 2. Publicar evento para outros serviços (Mensageria)
                evento_dados = {
                    "compra_id": db_payment.id,
                    "usuario_id": db_payment.usuario_id,
                    "publicacao_id": vaga.publicacao_id if vaga else None,
                    "valor": float(db_payment.valor_pago),
                    "status": "aprovada"
                }
                messaging_service.publicar_evento_compra(evento_dados)
                
                db.commit()
        
        elif payment_status in ["rejected", "cancelled", "refunded"]:
            db_payment.status = payment_status
            db.commit()

        LogService.log_event(
            db=db,
            tipo_evento=f"pagamento_{payment_status}",
            descricao=f"Webhook recebido: Status {payment_status} para compra {db_payment.id}",
            usuario_id=db_payment.usuario_id,
            entidade_id=db_payment.id,
            entidade_tipo="Compra"
        )

    return {"status": "ok"}