from typing import Optional, List, Union
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from decimal import Decimal

# --- Autenticação e Usuário ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    nome_completo: Optional[str] = None
    orcid_id: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nome_completo: Optional[str] = None

class UserAdminUpdate(UserUpdate):
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class User(UserBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

# --- Publicação ---
class PublicacaoBase(BaseModel):
    titulo: str
    subtitulo: Optional[str] = None
    descricao: Optional[str] = None
    ano_publicacao: Optional[int] = None
    tipo: Optional[str] = "livro"
    issn_isbn: Optional[str] = None

class PublicacaoCreate(PublicacaoBase):
    pass

class PublicacaoUpdate(PublicacaoBase):
    titulo: Optional[str] = None

class Publicacao(PublicacaoBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

# --- Vaga ---
class VagaBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    preco: Decimal
    quantidade_total: int

class VagaCreate(VagaBase):
    pass

class VagaUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    preco: Optional[Decimal] = None
    quantidade_total: Optional[int] = None
    ativa: Optional[bool] = None

class Vaga(VagaBase):
    id: UUID
    publicacao_id: UUID
    quantidade_disponivel: int
    ativa: bool
    model_config = ConfigDict(from_attributes=True)

# --- Versão ---
class VersaoBase(BaseModel):
    numero_versao: str

class Versao(VersaoBase):
    id: UUID
    publicacao_id: UUID
    data_upload: datetime
    caminho_arquivo_s3: str
    model_config = ConfigDict(from_attributes=True)