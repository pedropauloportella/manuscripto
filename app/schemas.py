# app/schemas.py
# Propósito: Definir os schemas Pydantic para validação e serialização de dados.
# Estes schemas são usados para requests (entrada) e responses (saída) da API.
# Variáveis de ambiente importantes: Nenhuma.

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# --- Schemas Comuns ---
class Msg(BaseModel):
    """Schema para mensagens genéricas da API."""
    msg: str

# --- Schemas de Usuário (User) ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    hashed_password: str # Será preenchido com a senha hash
    # Não pedimos orcid_id na criação direta, ele é vinculado via OAuth

class UserUpdate(UserBase):
    hashed_password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserInDBBase(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    orcid_id: Optional[str] = None

    class Config:
        from_attributes = True # Permite que Pydantic leia dados de um objeto ORM

# UserInDB para operações que precisam incluir o hashed_password (ex: autenticação interna)
class UserInDB(UserInDBBase):
    hashed_password: str

# User para resposta da API (não expõe o hashed_password)
class User(UserInDBBase):
    pass

# --- Schemas de Autenticação (JWT) ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None # No nosso caso, o email

# --- Schemas ORCID ---
class ORCIDProfile(BaseModel):
    """Schema para os dados do perfil ORCID recebidos após a autenticação."""
    orcid: str
    name: str
    email: Optional[str] = None
    # Adicione outros campos do perfil ORCID conforme necessário

# --- Schemas de Publicação ---
class PublicacaoBase(BaseModel):
    titulo: str = Field(..., example="A Pesquisa em Inteligência Artificial")
    subtitulo: Optional[str] = Field(None, example="Fundamentos e Aplicações")
    descricao: Optional[str] = Field(None, example="Uma obra abrangente sobre IA.")
    ano_publicacao: int = Field(..., example=2023)
    tipo: str = Field(..., example="livro", description="Tipo de publicação (livro, artigo, dossiê, capítulo)")
    issn_isbn: Optional[str] = Field(None, example="978-85-00000-00-0", description="ISSN ou ISBN, se aplicável")

class PublicacaoCreate(PublicacaoBase):
    pass

class PublicacaoUpdate(PublicacaoBase):
    titulo: Optional[str] = None
    ano_publicacao: Optional[int] = None
    tipo: Optional[str] = None

class VagaResponseForPublicacao(BaseModel):
    id: int
    titulo: str
    preco: float
    quantidade_disponivel: int
    ativa: bool

    class Config:
        from_attributes = True

class Publicacao(PublicacaoBase):
    id: int
    data_criacao: datetime
    data_atualizacao: datetime
    vagas: List[VagaResponseForPublicacao] = [] # Incluir vagas na resposta da publicação

    class Config:
        from_attributes = True

# --- Schemas de Vaga ---
class VagaBase(BaseModel):
    publicacao_id: int = Field(..., example=1)
    titulo: str = Field(..., example="Capítulo 1: Introdução à IA")
    descricao: Optional[str] = Field(None, example="Vaga para coautoria no capítulo introdutório.")
    preco: float = Field(..., gt=0, example=1500.00)
    quantidade_total: int = Field(..., gt=0, example=5)
    quantidade_disponivel: int = Field(..., gt=0, example=5)
    ativa: bool = Field(True, example=True)

class VagaCreate(VagaBase):
    pass

class VagaUpdate(VagaBase):
    titulo: Optional[str] = None
    publicacao_id: Optional[int] = None # Não permitir mudança de publicação após criação
    quantidade_total: Optional[int] = None
    quantidade_disponivel: Optional[int] = None
    preco: Optional[float] = None
    ativa: Optional[bool] = None

class PublicacaoResponseForVaga(BaseModel):
    id: int
    titulo: str
    tipo: str

    class Config:
        from_attributes = True

class Vaga(VagaBase):
    id: int
    data_criacao: datetime
    data_atualizacao: datetime
    publicacao: PublicacaoResponseForVaga # Incluir detalhes da publicação

    class Config:
        from_attributes = True