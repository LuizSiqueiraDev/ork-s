import sys
sys.path.append("..")

from fastapi import Depends, HTTPException, APIRouter
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models

router = APIRouter(
    prefix="/resultados",
    tags=["Resultados"],
    responses={404: {"descrição": "Não encontrado."}}
)

models.Base.metadata.create_all(bind=engine)


def obter_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Resultado(BaseModel):
    descricao: str
    completo: bool
    dono_id: int


@router.get("/")
async def mostrar_resultados(db: Session = Depends(obter_db)):
    return db.query(models.Resultados).all()


@router.get("/{re_id}")
async def mostrar_resultado(re_id: int, db: Session = Depends(obter_db)):
    modelo = db.query(models.Resultados).filter(models.Resultados.id == re_id).first()

    if modelo is not None:
        return modelo
    raise resultado_nao_encontrado()


@router.post("/")
async def criar_resultado(re: Resultado, db: Session = Depends(obter_db)):
    modelo = models.Resultados()
    modelo.descricao = re.descricao
    modelo.completo = re.completo
    modelo.dono_id = re.dono_id

    db.add(modelo)
    db.commit()

    return status_sucesso()


@router.put("/{re_id}")
async def atualizar_resultado(re_id: int, re: Resultado, db: Session = Depends(obter_db)):
    modelo = db.query(models.Resultados).filter(models.Resultados.id == re_id).first()

    if modelo is None:
        raise resultado_nao_encontrado()
    
    modelo.descricao = re.descricao
    modelo.completo = re.completo
    modelo.dono_id = re.dono_id

    db.add(modelo)
    db.commit()

    return status_sucesso()


@router.delete("/{re_id}")
async def deletar_resultado(re_id: int, db: Session = Depends(obter_db)):
    modelo = db.query(models.Resultados).filter(models.Resultados.id == re_id).first()

    if modelo is None:
        raise resultado_nao_encontrado()
    
    db.query(models.Resultados).filter(models.Resultados.id == re_id).delete()

    db.commit()

    return status_sucesso()


def resultado_nao_encontrado():
    return HTTPException(status_code=404, detail="Resultado não contrado.")

def status_sucesso():
    return {'status': 200, 'operação': 'sucedida'}