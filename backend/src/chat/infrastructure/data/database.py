"""database.py - Equiv. AppDbContext.cs. Modelos ORM e config do banco."""
from sqlalchemy import create_engine, Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./chatbot.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ConversaModel(Base):
    __tablename__ = "conversas"
    id = Column(String, primary_key=True)
    usuario_id = Column(String, nullable=False, index=True)
    titulo = Column(String, default="Nova Conversa")
    criado_em = Column(DateTime, default=datetime.now)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    mensagens = relationship("MensagemModel", back_populates="conversa", cascade="all, delete-orphan")


class MensagemModel(Base):
    __tablename__ = "mensagens"
    id = Column(String, primary_key=True)
    conversa_id = Column(String, ForeignKey("conversas.id"), nullable=False, index=True)
    conteudo = Column(Text, nullable=False)
    remetente = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    conversa = relationship("ConversaModel", back_populates="mensagens")


class ConhecimentoModel(Base):
    __tablename__ = "conhecimentos"
    id = Column(String, primary_key=True)
    titulo = Column(String, nullable=False)
    conteudo = Column(Text, nullable=False)
    fonte = Column(String, nullable=False)
    categoria = Column(String, nullable=False, index=True)
    criado_em = Column(DateTime, default=datetime.now)


def criar_tabelas():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
