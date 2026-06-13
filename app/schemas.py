from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# Schemas de Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[str] = None

# Schemas de Usuário
class UserBase(BaseModel):
    email: EmailStr
    nome_completo: Optional[str] = None
    orcid_id: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

# Schemas de Vaga
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

    class Config:
        from_attributes = True

# Schemas de Publicação
class PublicacaoBase(BaseModel):
    titulo: str
    subtitulo: Optional[str] = None
    descricao: Optional[str] = None
    ano_publicacao: int
    tipo: str # Ex: "livro", "artigo"
    issn_isbn: Optional[str] = None

class PublicacaoCreate(PublicacaoBase):
    pass

class Publicacao(PublicacaoBase):
    id: int
    vagas: List[Vaga] = []

    class Config:
        from_attributes = True