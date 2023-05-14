from fastapi import FastAPI
from database import engine
import models
import resultados, objetivos, autenticacao, usuarios

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(autenticacao.router)
app.include_router(objetivos.router)
app.include_router(resultados.router)