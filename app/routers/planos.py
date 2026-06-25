from fastapi import APIRouter
from app.database import get_connection

router = APIRouter(prefix="/planos", tags=["Planos"])

@router.get("/")
def listar_planos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT idplano, nomeplano, valorplano, duracao FROM planos ORDER BY idplano")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "nome": r[1], "valor": r[2], "duracao_dias": r[3]} for r in rows]