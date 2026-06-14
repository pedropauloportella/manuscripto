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
        try:
            # Bloqueia por 5 segundos esperando uma mensagem
            resultado = messaging_service.redis_client.brpop("eventos_compra", timeout=5)
            
            if resultado:
                _, mensagem = resultado
                dados = json.loads(mensagem)
                
                print(f"[{time.strftime('%H:%M:%S')}] [WORKER] Processando Compra: {dados['compra_id']}")
                
                # Lógica de negócio assíncrona (Ex: Integração com ERP ou Gerador de PDF)
                # ...
                
                time.sleep(1) # Simula delay
                print(f"[WORKER] Sucesso: Evento {dados['compra_id']} processado.")

        except Exception as e:
            print(f"[WORKER] [ERRO] Falha ao processar evento: {e}")
            # Espera um pouco antes de tentar novamente para não sobrecarregar em caso de erro de rede
            time.sleep(5)

if __name__ == "__main__":
    processar_eventos()