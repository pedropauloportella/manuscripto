class EmailService:
    """
    Serviço responsável pelo envio de notificações por e-mail.
    """
    @staticmethod
    def enviar_confirmacao_coautoria(email_destino: str, nome_usuario: str, titulo_obra: str):
        """
        Simula o envio de um e-mail de boas-vindas ao novo coautor.
        """
        assunto = f"Bem-vindo à coautoria de {titulo_obra}"
        mensagem = (
            f"Olá {nome_usuario},\n\n"
            f"Seu pagamento foi confirmado! Agora você é oficialmente um coautor da obra '{titulo_obra}'.\n"
            "Acesse seu painel para enviar novas versões do manuscrito."
        )
        # Aqui entraria a lógica de integração com SMTP ou API de e-mail
        print(f"--- SIMULAÇÃO DE E-MAIL ---\nPara: {email_destino}\nAssunto: {assunto}\nCorpo: {mensagem}\n---------------------------")

email_service = EmailService()