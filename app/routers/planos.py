# app/routers/planos.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/planos", tags=["Planos"])


class PlanoResponse(BaseModel):
    id: int
    nome: str
    valor: float
    duracao_dias: int


@router.get("/", response_model=list[PlanoResponse])
def listar_planos(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    offset = (page - 1) * limit
    rows = db.execute(
        text("SELECT idplano, nomeplano, valorplano, duracao FROM planos ORDER BY idplano LIMIT :limit OFFSET :offset"),
        {"limit": limit, "offset": offset}
    ).fetchall()
    return [{"id": r[0], "nome": r[1], "valor": r[2], "duracao_dias": r[3]} for r in rows]