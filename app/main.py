from fastapi import FastAPI
from app.routers import alunos, planos, matriculas, pagamentos

app = FastAPI(
    title="Academia API",
    description="API REST para gerenciamento de academia",
    version="1.0.0"
)

app.include_router(alunos.router)
app.include_router(planos.router)
app.include_router(matriculas.router)
app.include_router(pagamentos.router)


@app.get("/")
def root():
    return {"message": "Academia API funcionando!"}