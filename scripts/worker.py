import json
import time
from app.services.messaging_service import messaging_service

def processar_eventos():
    """
    Consome eventos da fila do Redis de forma contínua.
    Simula um serviço externo (ex: Contabilidade ou Analytics).
    """
    print("[WORKER] Iniciando consumidor de eventos...")
    
    while True:
        # BRPOP remove e retorna o último elemento da lista, bloqueando se estiver vazia
        # O timeout de 0 significa que ele espera indefinidamente
        resultado = messaging_service.redis_client.brpop("eventos_compra", timeout=5)
        
        if resultado:
            _, mensagem = resultado
            dados = json.loads(mensagem)
            
            print(f"\n[WORKER] >>> Processando Evento Externo")
            print(f"[WORKER] Compra ID: {dados['compra_id']}")
            print(f"[WORKER] Usuário ID: {dados['usuario_id']}")
            print(f"[WORKER] Valor: R$ {dados['valor']}")
            print(f"[WORKER] Ação: Gerando contrato digital e atualizando dashboard de vendas...")
            
            # Simula processamento pesado
            time.sleep(1)

if __name__ == "__main__":
    processar_eventos()