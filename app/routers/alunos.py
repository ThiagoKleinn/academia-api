from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import get_connection

router = APIRouter(prefix="/alunos", tags=["Alunos"])

class AlunoCreate(BaseModel):
    cpf: str
    nomecliente: str

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
def buscar_aluno(id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT idaluno, cpf, nomecliente FROM alunos WHERE idaluno = %s", (id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return {"id": row[0], "cpf": row[1], "nome": row[2]}

@router.post("/", status_code=201)
def criar_aluno(aluno: AlunoCreate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO alunos (cpf, nomecliente) VALUES (%s, %s) RETURNING idaluno",
            (aluno.cpf, aluno.nomecliente)
        )
        novo_id = cur.fetchone()[0]
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"id": novo_id, "cpf": aluno.cpf, "nome": aluno.nomecliente}

@router.put("/{id}")
def atualizar_aluno(id: int, aluno: AlunoCreate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT idaluno FROM alunos WHERE idaluno = %s", (id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    try:
        cur.execute(
            "UPDATE alunos SET cpf = %s, nomecliente = %s WHERE idaluno = %s",
            (aluno.cpf, aluno.nomecliente, id)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"id": id, "cpf": aluno.cpf, "nome": aluno.nomecliente}

@router.delete("/{id}", status_code=204)
def deletar_aluno(id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT idaluno FROM alunos WHERE idaluno = %s", (id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    cur.execute("DELETE FROM alunos WHERE idaluno = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()