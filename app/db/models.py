from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Tabela associativa para Coautoria (conforme requisito do MVP)
publication_authors = Table(
    "publication_authors",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("publication_id", ForeignKey("publications.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    orcid_id = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True) # Pode ser nulo se usar apenas OAuth

class Publication(Base):
    __tablename__ = "publications"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    type = Column(String)  # livro, artigo, etc.
    price = Column(Float, default=0.0)
    is_open_vacancy = Column(Boolean, default=True)
    
    authors = relationship("User", secondary=publication_authors, backref="publications")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    mp_preference_id = Column(String, index=True)
    status = Column(String) # pending, approved, rejected
    user_id = Column(Integer, ForeignKey("users.id"))
    publication_id = Column(Integer, ForeignKey("publications.id"))
    
    user = relationship("User")
    publication = relationship("Publication")