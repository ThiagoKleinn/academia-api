from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.database import get_connection

router = APIRouter(prefix="/matriculas", tags=["Matrículas"])

class MatriculaCreate(BaseModel):
    idaluno: int
    idplano: int
    idpersonal: Optional[int] = None
    datainicio: date
    datafim: Optional[date] = None

@router.get("/")
def listar_matriculas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.idmatricula, a.nomecliente, p.nomeplano, m.datainicio, m.datafim
        FROM matriculas m
        JOIN alunos a ON m.idaluno = a.idaluno
        JOIN planos p ON m.idplano = p.idplano
        ORDER BY m.idmatricula
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "aluno": r[1], "plano": r[2], "inicio": r[3], "fim": r[4]} for r in rows]

@router.get("/{id}")
def buscar_matricula(id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.idmatricula, a.nomecliente, p.nomeplano, m.datainicio, m.datafim
        FROM matriculas m
        JOIN alunos a ON m.idaluno = a.idaluno
        JOIN planos p ON m.idplano = p.idplano
        WHERE m.idmatricula = %s
    """, (id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")
    return {"id": row[0], "aluno": row[1], "plano": row[2], "inicio": row[3], "fim": row[4]}

@router.post("/", status_code=201)
def criar_matricula(matricula: MatriculaCreate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO matriculas (idaluno, idplano, idpersonal, datainicio, datafim)
            VALUES (%s, %s, %s, %s, %s) RETURNING idmatricula
        """, (matricula.idaluno, matricula.idplano, matricula.idpersonal, matricula.datainicio, matricula.datafim))
        novo_id = cur.fetchone()[0]
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"id": novo_id, **matricula.dict()}

@router.delete("/{id}", status_code=204)
def deletar_matricula(id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT idmatricula FROM matriculas WHERE idmatricula = %s", (id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")
    cur.execute("DELETE FROM matriculas WHERE idmatricula = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()