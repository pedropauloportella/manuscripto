from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from decimal import Decimal

# --- Autenticação e Usuário ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    nome_completo: Optional[str] = None
    orcid_id: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserUpdate(BaseModel):
    nome_completo: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class User(UserBase):
    id: int
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
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Vaga ---
class VagaBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    preco: Decimal
    quantidade_total: int

class VagaCreate(VagaBase):
    pass

class Vaga(VagaBase):
    id: int
    publicacao_id: int
    quantidade_disponivel: int
    ativa: bool
    model_config = ConfigDict(from_attributes=True)

# --- Versão ---
class VersaoBase(BaseModel):
    numero_versao: str

class Versao(VersaoBase):
    id: int
    publicacao_id: int
    data_upload: datetime
    caminho_arquivo_s3: str
    model_config = ConfigDict(from_attributes=True)