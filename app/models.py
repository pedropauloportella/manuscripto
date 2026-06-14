from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Boolean, DateTime, Text, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class Usuario(Base):
    __tablename__ = "usuario"
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    nome_completo = Column(String)
    orcid_id = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    publicacoes = relationship("AutorPublicacao", back_populates="usuario")
    compras = relationship("Compra", back_populates="usuario")
    logs = relationship("LogEvento", back_populates="usuario")

class Publicacao(Base):
    __tablename__ = "publicacao"
    titulo = Column(String, index=True, nullable=False)
    subtitulo = Column(String)
    descricao = Column(Text)
    ano_publicacao = Column(Integer)
    tipo = Column(String) # livro, artigo, etc.
    issn_isbn = Column(String)
    
    vagas = relationship("Vaga", back_populates="publicacao")
    autores = relationship("AutorPublicacao", back_populates="publicacao")
    versoes = relationship("Versao", back_populates="publicacao")

class Vaga(Base):
    __tablename__ = "vaga"
    publicacao_id = Column(UUID, ForeignKey("publicacao.id"))
    titulo = Column(String, nullable=False)
    descricao = Column(Text)
    preco = Column(Numeric(10, 2), nullable=False)
    quantidade_total = Column(Integer, nullable=False)
    quantidade_disponivel = Column(Integer)
    ativa = Column(Boolean, default=True)
    
    publicacao = relationship("Publicacao", back_populates="vagas")

class Compra(Base):
    __tablename__ = "compra"
    usuario_id = Column(UUID, ForeignKey("usuario.id"))
    vaga_id = Column(UUID, ForeignKey("vaga.id"))
    data_compra = Column(DateTime, default=datetime.utcnow)
    valor_pago = Column(Numeric(10, 2))
    status = Column(String) # pendente, aprovada, cancelada
    mp_preference_id = Column(String, index=True)
    id_pagamento_mp = Column(String)
    
    usuario = relationship("Usuario", back_populates="compras")
    vaga = relationship("Vaga")

class AutorPublicacao(Base):
    __tablename__ = "autor_publicacao"
    usuario_id = Column(UUID, ForeignKey("usuario.id"))
    publicacao_id = Column(UUID, ForeignKey("publicacao.id"))
    compra_id = Column(UUID, ForeignKey("compra.id"), nullable=True)
    funcao = Column(String) # autor, coautor, organizador
    
    usuario = relationship("Usuario", back_populates="publicacoes")
    publicacao = relationship("Publicacao", back_populates="autores")

class Versao(Base):
    __tablename__ = "versao"
    publicacao_id = Column(UUID, ForeignKey("publicacao.id"))
    numero_versao = Column(String, nullable=False)
    data_upload = Column(DateTime, default=datetime.utcnow)
    caminho_arquivo_s3 = Column(String, nullable=False)
    
    publicacao = relationship("Publicacao", back_populates="versoes")

class LogEvento(Base):
    __tablename__ = "log_evento"
    tipo_evento = Column(String, nullable=False) # login, upload, compra, etc.
    descricao = Column(Text)
    data_evento = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(UUID, ForeignKey("usuario.id"), nullable=True)
    entidade_id = Column(UUID, nullable=True) # ID da vaga, publicacao, etc.
    entidade_tipo = Column(String, nullable=True)
    
    usuario = relationship("Usuario", back_populates="logs")