import sys
sys.path.append("..")

from fastapi import Depends, APIRouter, HTTPException
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from resultados import status_sucesso
import models
from autenticacao import obter_usuario_atual, credencial_de_excessao_usuario

router = APIRouter(
    prefix="/objetivos",
    tags=["Objetivos"],
    responses={404: {"descrição": "Não encontrado."}}
)

models.Base.metadata.create_all(bind=engine)


def obter_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Objetivo(BaseModel):
    descricao: str
    porcentagem: str
    dono_id: int


@router.get("/usuario")
async def mostrar_por_usuario(usuario: dict = Depends(obter_usuario_atual), db: Session = Depends(obter_db)):
    if usuario is None:
        raise credencial_de_excessao_usuario()
    return db.query(models.Objetivos).filter(models.Objetivos.dono_id == usuario.get("id")).all()


@router.get("/")
async def mostrar_objetivos(db: Session = Depends(obter_db)):
    return db.query(models.Objetivos).all()


@router.get("/{ob_id}")
async def mostrar_objetivo(ob_id: int, usuario: dict = Depends(obter_usuario_atual), db: Session = Depends(obter_db)):
    if usuario is None:
        raise credencial_de_excessao_usuario()
    
    modelo = db.query(models.Objetivos).filter(models.Objetivos.id == ob_id).filter(models.Objetivos.dono_id == usuario.get("id")).first()

    if modelo is not None:
        return modelo
    raise objetivo_nao_encontrado()

@router.post("/")
async def criar_objetivo(ob: Objetivo, usuario: dict = Depends(obter_usuario_atual), db: Session = Depends(obter_db)):
    if usuario is None:
        raise credencial_de_excessao_usuario()
    modelo = models.Objetivos()
    modelo.descricao = ob.descricao
    modelo.porcentagem = ob.porcentagem
    modelo.dono_id = usuario.get("id")

    db.add(modelo)
    db.commit()

    return status_sucesso()


@router.put("/{ob_id}")
async def atualizar_objetivo(ob_id: int, ob: Objetivo, usuario: dict = Depends(obter_usuario_atual), db: Session = Depends(obter_db)):
    modelo = db.query(models.Objetivos).filter(models.Objetivos.id == ob_id).filter(models.Objetivos.dono_id == usuario.get("id")).first()

    if modelo is None:
        raise objetivo_nao_encontrado()
    modelo.descricao = ob.descricao
    modelo.porcentagem = ob.porcentagem
    modelo.dono_id = ob.dono_id

    db.add(modelo)
    db.commit()

    return status_sucesso()


@router.delete("/{ob_id}")
async def deletar_objetivo(ob_id: int, db: Session = Depends(obter_db)):
    modelo = db.query(models.Objetivos).filter(models.Objetivos.id == ob_id).first()

    if modelo is None:
        raise objetivo_nao_encontrado()
    
    db.query(models.Objetivos).filter(models.Objetivos.id == ob_id).delete()

    db.commit()

    return status_sucesso()


def objetivo_nao_encontrado():
    return HTTPException(status_code=404, detail="Objetivo não encontrado.")