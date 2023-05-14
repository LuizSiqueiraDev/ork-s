import sys
sys.path.append("..")

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Usuarios(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    apelido = Column(String, unique=True, index=True)
    nome = Column(String)
    sobrenome = Column(String)
    senha_hashed = Column(String)
    ativo = Column(Boolean, default=True)

    objetivos = relationship("Objetivos", back_populates="dono")


class Objetivos(Base):
    __tablename__ = "objetivos"
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, index=True)
    porcentagem = Column(String, index=True)

    resultados = relationship("Resultados", back_populates="dono")
    dono_id = Column(Integer, ForeignKey("usuarios.id"))
    dono = relationship("Usuarios", back_populates="objetivos")


class Resultados(Base):
    __tablename__ = "resultados"
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String)
    completo = Column(Boolean, default=False)
    
    dono_id = Column(Integer, ForeignKey("objetivos.id"))
    dono = relationship("Objetivos", back_populates="resultados")