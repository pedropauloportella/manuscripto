import uuid
from decimal import Decimal
from sqlalchemy.orm import Session
from app import models

class SeedService:
    def __init__(self, db: Session):
        self.db = db

    def seed_data(self, admin_email: str, admin_id: uuid.UUID):
        print("Iniciando a criação de dados fictícios...")

        # 1. Criar Usuários
        users_to_create = [
            models.Usuario(
                id=admin_id,
                email=admin_email,
                nome_completo="Administrador Geral",
                role="admin",
                grau_formacao="Doutorado",
                is_superuser=True,
                is_active=True
            ),
            models.Usuario(
                id=uuid.uuid4(),
                email="editor@manuscripto.com",
                nome_completo="Editor Exemplo",
                role="editor",
                grau_formacao="Mestre",
                is_superuser=False,
                is_active=True
            ),
            models.Usuario(
                id=uuid.uuid4(),
                email="joao.silva@email.com",
                nome_completo="João Silva",
                role="autor",
                grau_formacao="Graduado",
                is_superuser=False,
                is_active=True
            ),
            models.Usuario(
                id=uuid.uuid4(),
                email="maria.oliveira@email.com",
                nome_completo="Maria Oliveira",
                role="autor",
                grau_formacao="Mestrando",
                is_superuser=False,
                is_active=True
            )
        ]

        for user_data in users_to_create:
            existing = self.db.query(models.Usuario).filter(models.Usuario.id == user_data.id).first()
            if not existing:
                self.db.add(user_data)
        self.db.flush() # Garante que os IDs existam antes de criar relações

        # 2. Criar Publicações
        pub1 = models.Publicacao(
            id=uuid.uuid4(),
            titulo="Inteligência Artificial na Educação Moderna",
            usuario_id=admin_id,
            subtitulo="Desafios e Oportunidades no Século XXI",
            descricao="Uma análise profunda sobre o impacto de LLMs em salas de aula.",
            tipo="livro",
            ano_publicacao=2024
        )
        pub2 = models.Publicacao(
            id=uuid.uuid4(),
            titulo="Sustentabilidade Urbana",
            usuario_id=admin_id,
            subtitulo="Cidades Verdes e o Futuro",
            descricao="Estudo de caso sobre mobilidade urbana sustentável em capitais brasileiras.",
            tipo="artigo",
            ano_publicacao=2023
        )
        
        self.db.add_all([pub1, pub2])
        self.db.flush() # Para garantir que os IDs existam para as vagas

        # 3. Criar Vagas para as Publicações
        vaga1 = models.Vaga(
            id=uuid.uuid4(),
            publicacao_id=pub1.id,
            titulo="Coautor - Capítulo de Metodologia",
            descricao="Busca-se pesquisador com experiência em análise quantitativa.",
            preco=Decimal("450.00"),
            quantidade_total=3,
            quantidade_disponivel=3,
            ativa=True
        )
        self.db.add(vaga1)

        self.db.commit()
        print("Banco de dados populado com sucesso!")

    def clear_data(self):
        print("Iniciando a remoção de dados fictícios...")
        # Ordem inversa de criação para evitar problemas de FK
        self.db.query(models.Vaga).delete()
        self.db.query(models.Publicacao).delete()
        self.db.query(models.AutorPublicacao).delete()
        self.db.query(models.Compra).delete()
        self.db.query(models.Versao).delete()
        self.db.query(models.LogEvento).delete()
        
        # Remove todos os usuários, exceto o admin (para não deslogar o superuser)
        # ou remove todos se o admin for recriado no seed
        # Por simplicidade, vamos remover todos os usuários criados pelo script,
        # exceto o admin que está logado.
        # Isso requer que o admin_id seja passado ou que o admin não seja deletado
        # Vamos deletar todos e o seed recria o admin.
        self.db.query(models.Usuario).delete()

        self.db.commit()
        print("Dados fictícios removidos com sucesso!")