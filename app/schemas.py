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
    cidade: Optional[str] = None
    universidade: Optional[str] = None
    area_formacao: Optional[str] = None
    lattes_link: Optional[str] = None
    linkedin_link: Optional[str] = None
    instagram_link: Optional[str] = None
    avatar_url: Optional[str] = None
    grau_formacao: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

# --- Publicação ---
class PublicacaoBase(BaseModel):
    titulo: str
    subtitulo: Optional[str] = None
    descricao: Optional[str] = None
    ano_publicacao: Optional[int] = None
    tipo: Optional[str] = "livro"
    issn_isbn: Optional[str] = None
    usuario_id: Optional[UUID] = None
    resumo: Optional[str] = None
    area_conhecimento: Optional[str] = None
    data_prevista_publicacao: Optional[datetime] = None
    tem_doi: bool = False
    tem_isbn: bool = False
    tem_issn: bool = False

class PublicacaoCreate(PublicacaoBase):
    pass

class PublicacaoUpdate(PublicacaoBase):
    titulo: Optional[str] = None

# --- Vaga ---
class VagaBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    preco: Decimal
    quantidade_total: int
    data_encerramento: Optional[datetime] = None
    pre_requisitos: Optional[str] = None
    imagem_url: Optional[str] = None # Novo campo

class VagaCreate(VagaBase):
    pass

class VagaUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    preco: Optional[Decimal] = None
    quantidade_total: Optional[int] = None
    ativa: Optional[bool] = None
    imagem_url: Optional[str] = None # Novo campo
    pre_requisitos: Optional[str] = None # Novo campo

class Vaga(VagaBase):
    id: UUID
    publicacao_id: UUID
    quantidade_disponivel: int
    ativa: bool
    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nome_completo: Optional[str] = None
    orcid_id: Optional[str] = None
    cidade: Optional[str] = None
    universidade: Optional[str] = None
    area_formacao: Optional[str] = None
    lattes_link: Optional[str] = None
    linkedin_link: Optional[str] = None
    instagram_link: Optional[str] = None
    avatar_url: Optional[str] = None
    grau_formacao: Optional[str] = None

class UserAdminUpdate(UserUpdate):
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class User(UserBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

# --- Schemas para Catálogo e Relacionamentos (com informações aninhadas) ---
# Define UsuarioInVagaCatalog antes de Publicacao e PublicacaoInVagaCatalog
class UsuarioInVagaCatalog(BaseModel):
    nome_completo: Optional[str] = None
    grau_formacao: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# Define PublicacaoInVagaCatalog antes de VagaCatalog
class PublicacaoInVagaCatalog(PublicacaoBase):
    id: UUID # PublicacaoInVagaCatalog também precisa de um ID
    criador: Optional[UsuarioInVagaCatalog] = None
    model_config = ConfigDict(from_attributes=True)

# Define Publicacao (que usa UsuarioInVagaCatalog)
class Publicacao(PublicacaoBase):
    id: UUID
    criador: Optional[UsuarioInVagaCatalog] = None
    model_config = ConfigDict(from_attributes=True)

# Define VagaCatalog (que usa PublicacaoInVagaCatalog)
class VagaCatalog(VagaBase):
    id: UUID
    publicacao_id: UUID
    quantidade_disponivel: int
    ativa: bool
    publicacao: PublicacaoInVagaCatalog
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