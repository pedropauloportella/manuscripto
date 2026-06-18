import uuid
from decimal import Decimal
from sqlalchemy.orm import Session
from app import models
from app.services.cache_service import cache_service

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
            # Verifica se o usuário já existe por ID ou Email para evitar duplicidade e erro 500
            existing = self.db.query(models.Usuario).filter(
                (models.Usuario.id == user_data.id) | 
                (models.Usuario.email == user_data.email)
            ).first()
            if not existing:
                self.db.add(user_data)
            else:
                # Se o usuário já existe, sincroniza o ID para as relações (AutorPublicacao) abaixo
                user_data.id = existing.id
        
        self.db.flush() # Garante que os estados existam antes de criar relações

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

        # 4. Vincular Autores às Publicações (AutorPublicacao)
        vinculos = [
            models.AutorPublicacao(
                usuario_id=users_to_create[2].id, # João Silva
                publicacao_id=pub1.id,
                funcao="autor"
            ),
            models.AutorPublicacao(
                usuario_id=users_to_create[3].id, # Maria Oliveira
                publicacao_id=pub1.id,
                funcao="coautor"
            )
        ]
        self.db.add_all(vinculos)

        self.db.commit()
        print("Banco de dados populado com sucesso!")

    def clear_data(self):
        print("Iniciando a remoção seletiva de dados fictícios...")
        
        # Identificadores únicos dos dados criados pelo seed
        seed_emails = ["editor@manuscripto.com", "joao.silva@email.com", "maria.oliveira@email.com"]
        seed_titles = ["Inteligência Artificial na Educação Moderna", "Sustentabilidade Urbana"]

        # 1. Identificar IDs para deleção cirúrgica
        user_ids = [u.id for u in self.db.query(models.Usuario.id).filter(models.Usuario.email.in_(seed_emails)).all()]
        pub_ids = [p.id for p in self.db.query(models.Publicacao.id).filter(models.Publicacao.titulo.in_(seed_titles)).all()]
        vaga_ids = [v.id for v in self.db.query(models.Vaga.id).filter(models.Vaga.publicacao_id.in_(pub_ids)).all()]

        # 2. Deletar em ordem rigorosa (FK constraints) usando filtros específicos
        self.db.query(models.LogEvento).filter(
            (models.LogEvento.usuario_id.in_(user_ids)) | (models.LogEvento.entidade_id.in_(pub_ids))
        ).delete(synchronize_session=False)

        self.db.query(models.AutorPublicacao).filter(
            (models.AutorPublicacao.usuario_id.in_(user_ids)) | (models.AutorPublicacao.publicacao_id.in_(pub_ids))
        ).delete(synchronize_session=False)

        self.db.query(models.Versao).filter(models.Versao.publicacao_id.in_(pub_ids)).delete(synchronize_session=False)

        self.db.query(models.Compra).filter(
            (models.Compra.usuario_id.in_(user_ids)) | (models.Compra.vaga_id.in_(vaga_ids))
        ).delete(synchronize_session=False)

        self.db.query(models.Vaga).filter(models.Vaga.id.in_(vaga_ids)).delete(synchronize_session=False)
        self.db.query(models.Publicacao).filter(models.Publicacao.id.in_(pub_ids)).delete(synchronize_session=False)
        
        # Deletar usuários (o admin nunca entra aqui pois seu email não está em seed_emails)
        self.db.query(models.Usuario).filter(models.Usuario.id.in_(user_ids)).delete(synchronize_session=False)

        self.db.commit()
        # Limpa o cache global para garantir que dados de teste não persistam na UI
        cache_service.flush_all()
        print("Dados fictícios removidos com sucesso!")