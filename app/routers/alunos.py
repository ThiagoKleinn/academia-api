from fastapi import APIRouter, HTTPException
from app.database import get_connection

router = APIRouter(prefix = "/alunos", tags=["Alunos"])

@router.get("/")
def listar_alunos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT idaluno, cpf, nomecliente FROM alunos ORDER BY idaluno")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "cpf": r[1], "nome": r[2]} for r in rows]

@router.get("/{id}")
def buscaraluno(id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT idaluno, cpf, nomecliente FROM alunos WHERE idaluno = %s", (id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return {"id": row[0], "cpf": row[1], "nome": row[2]}