
from app.db.base_class import Base  # Importa a Base declarativa personalizada

from sqlalchemy import String, Boolean, Integer, ForeignKey, DateTime, func, Text, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

class Usuario(Base):
    __tablename__ = "usuario"

    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    nome_completo: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    orcid_id: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True, nullable=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relacionamento com Publicacao (se for autor/editor de Publicações)
    publicacoes: Mapped[List["AutorPublicacao"]] = relationship(back_populates="autor")
    # Relacionamento com Compra
    compras: Mapped[List["Compra"]] = relationship(back_populates="comprador")

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, email='{self.email}', orcid_id='{self.orcid_id}')>"

class Publicacao(Base):
    """
    Modelo para representar uma publicação (livro, capítulo, artigo, dossiê, etc.).
    """
    __tablename__ = "publicacao"

    titulo: Mapped[str] = mapped_column(String, index=True)
    subtitulo: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ano_publicacao: Mapped[int] = mapped_column(Integer)
    tipo: Mapped[str] = mapped_column(String) # Ex: "livro", "artigo", "dossie", "capitulo"
    issn_isbn: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    data_criacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    data_atualizacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    vagas: Mapped[List["Vaga"]] = relationship(back_populates="publicacao", cascade="all, delete-orphan")
    autores: Mapped[List["AutorPublicacao"]] = relationship(back_populates="publicacao", cascade="all, delete-orphan")
    versoes: Mapped[List["Versao"]] = relationship(back_populates="publicacao", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Publicacao(id={self.id}, titulo='{self.titulo}', tipo='{self.tipo}')>"

class Vaga(Base):
    """
    Modelo para representar uma vaga disponível em uma publicação.
    """
    __tablename__ = "vaga"

    publicacao_id: Mapped[int] = mapped_column(ForeignKey("publicacao.id"))
    titulo: Mapped[str] = mapped_column(String, index=True)
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preco: Mapped[float] = mapped_column(DECIMAL(10, 2))
    quantidade_total: Mapped[int] = mapped_column(Integer)
    quantidade_disponivel: Mapped[int] = mapped_column(Integer)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)
    data_criacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    data_atualizacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    publicacao: Mapped["Publicacao"] = relationship(back_populates="vagas")
    compras: Mapped[List["Compra"]] = relationship(back_populates="vaga")

    def __repr__(self) -> str:
        return f"<Vaga(id={self.id}, titulo='{self.titulo}', publicacao_id={self.publicacao_id})>"

class Compra(Base):
    """
    Modelo para registrar a compra de uma vaga por um usuário.
    """
    __tablename__ = "compra"

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    vaga_id: Mapped[int] = mapped_column(ForeignKey("vaga.id"))
    data_compra: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    valor_pago: Mapped[float] = mapped_column(DECIMAL(10, 2))
    status: Mapped[str] = mapped_column(String, default="pendente") # Ex: "pendente", "aprovada", "rejeitada", "cancelada"
    id_pagamento_mp: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True) # ID da transação no MercadoPago

    # Relacionamentos
    comprador: Mapped["Usuario"] = relationship(back_populates="compras")
    vaga: Mapped["Vaga"] = relationship(back_populates="compras")
    autor_vinculado: Mapped[Optional["AutorPublicacao"]] = relationship(back_populates="compra_origem", uselist=False)

    def __repr__(self) -> str:
        return f"<Compra(id={self.id}, usuario_id={self.usuario_id}, vaga_id={self.vaga_id}, status='{self.status}')>"

class AutorPublicacao(Base):
    """
    Modelo de associação para vincular autores a publicações (muitos-para-muitos com dados extras).
    Representa o coautor de uma publicação, podendo ser resultado de uma compra.
    """
    __tablename__ = "autor_publicacao"

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), primary_key=True)
    publicacao_id: Mapped[int] = mapped_column(ForeignKey("publicacao.id"), primary_key=True)
    compra_id: Mapped[Optional[int]] = mapped_column(ForeignKey("compra.id"), unique=True, nullable=True) # Opcional, se a vaga foi comprada
    funcao: Mapped[str] = mapped_column(String, default="autor") # Ex: "autor", "editor", "coautor"
    data_vinculo: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    autor: Mapped["Usuario"] = relationship(back_populates="publicacoes")
    publicacao: Mapped["Publicacao"] = relationship(back_populates="autores")
    compra_origem: Mapped[Optional["Compra"]] = relationship(back_populates="autor_vinculado")

    def __repr__(self) -> str:
        return f"<AutorPublicacao(usuario_id={self.usuario_id}, publicacao_id={self.publicacao_id}, funcao='{self.funcao}')>"

class Versao(Base):
    """
    Modelo para gerenciar diferentes versões do conteúdo de uma publicação.
    """
    __tablename__ = "versao"

    publicacao_id: Mapped[int] = mapped_column(ForeignKey("publicacao.id"))
    numero_versao: Mapped[str] = mapped_column(String) # Ex: "1.0", "1.1", "2.0"
    caminho_arquivo_s3: Mapped[str] = mapped_column(String)
    data_upload: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # TODO: Adicionar hash do arquivo para verificação de integridade

    # Relacionamentos
    publicacao: Mapped["Publicacao"] = relationship(back_populates="versoes")

    def __repr__(self) -> str:
        return f"<Versao(id={self.id}, publicacao_id={self.publicacao_id}, numero_versao='{self.numero_versao}')>"

class LogEvento(Base):
    """
    Modelo para registrar eventos importantes no sistema, como transações, erros, etc.
    """
    __tablename__ = "log_evento"

    tipo_evento: Mapped[str] = mapped_column(String) # Ex: "compra", "upload", "erro_mp", "login"
    descricao: Mapped[str] = mapped_column(Text)
    data_evento: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    usuario_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuario.id"), nullable=True)
    entidade_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # ID da entidade relacionada (ex: Compra.id, Publicacao.id)
    entidade_tipo: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Tipo da entidade (ex: "Compra", "Publicacao")

    # Relacionamentos (opcional, dependendo do uso)
    usuario: Mapped[Optional["Usuario"]] = relationship()

    def __repr__(self) -> str:
        return f"<LogEvento(id={self.id}, tipo='{self.tipo_evento}', data='{self.data_evento}')>"
