import sys
sys.path.append("..")

from fastapi import Depends, APIRouter, HTTPException, status
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from resultados import status_sucesso
import models
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"],
    responses={404: {"descrição": "Não encontrado."}}
)

models.Base.metadata.create_all(bind=engine)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")



def obter_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class CriarUsuario(BaseModel):
    email: str
    apelido: str
    nome: str
    sobrenome: str
    senha: str
    

def obter_senha_hash(senha):
    return bcrypt_context.hash(senha)


def verificar_senha(senha_simples, senha_hashed):
    return bcrypt_context.verify(senha_simples, senha_hashed)


def autentificar_usuario(apelido: str, senha: str, db):
    usuario = db.query(models.Usuarios).filter(models.Usuarios.apelido == apelido).first()

    if not usuario:
        return False
    if not verificar_senha(senha, usuario.senha_hashed):
        return False
    return usuario


def criar_acesso_token(apelido: str, usuario_id: int, expirar_delta: timedelta|None = None):
    codificar = {"sub": apelido, "id": usuario_id}

    if expirar_delta:
        expirar = datetime.utcnow() + expirar_delta
    else:
        expirar =datetime.utcnow() + timedelta(minutes=30)
    codificar.update({"exp": expirar})
    return jwt.encode(codificar, SECRET_KEY, algorithm=ALGORITHM)


async def obter_usuario_atual(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        apelido: str = payload.get("sub")
        usuario_id: int = payload.get("id")
        
        if apelido is None or usuario_id is None:
            raise credencial_de_excessao_usuario()
        return {"apelido": apelido, "id": usuario_id}
    except JWTError:
        raise credencial_de_excessao_usuario()


@router.post("/criar/usuario")
async def criar_novo_usuario(criar_usuario: CriarUsuario, db: Session = Depends(obter_db)):
    modelo = models.Usuarios()
    modelo.email = criar_usuario.email
    modelo.apelido = criar_usuario.apelido
    modelo.nome = criar_usuario.nome
    modelo.sobrenome = criar_usuario.sobrenome

    senha_hash = obter_senha_hash(criar_usuario.senha)
    modelo.senha_hashed = senha_hash

    modelo.ativo = True

    db.add(modelo)
    db.commit()

    return status_sucesso()


@router.post("/token")
async def login_de_acesso_do_token(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(obter_db)):
    usuario = autentificar_usuario(form.username, form.password, db)

    if not usuario:
        raise excecao_do_token()
    expirar_token = timedelta(minutes=(30))
    token = criar_acesso_token(usuario.apelido, usuario.id, expirar_delta=expirar_token)
    return {"token": token}
    

# Exceções
def credencial_de_excessao_usuario():
    credencial_de_excecao = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não pode validar a credencial.",
        headers={"WWW-Autenticado": "Portador"},
    )
    return credencial_de_excecao


def excecao_do_token():
    resposta_de_excecao_do_token = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Usuário ou senha incorreta.",
        headers={"WWW-Autenticado": "Portador"},
    )
    return resposta_de_excecao_do_token