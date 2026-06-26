# matriculas.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.database import get_connection
from app.auth import get_current_user

router = APIRouter(prefix="/matriculas", tags=["Matrículas"])


class MatriculaCreate(BaseModel):
    idaluno: int
    idplano: int
    idpersonal: Optional[int] = None
    datainicio: date
    datafim: Optional[date] = None


class MatriculaResponse(BaseModel):
    id: int
    aluno: str
    plano: str
    inicio: date
    fim: Optional[date] = None


@router.get("/", response_model=list[MatriculaResponse])
def listar_matriculas(current_user: str = Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT m.idmatricula, a.nomecliente, p.nomeplano, m.datainicio, m.datafim
            FROM matriculas m
            JOIN alunos a ON m.idaluno = a.idaluno
            JOIN planos p ON m.idplano = p.idplano
            ORDER BY m.idmatricula
        """)
        rows = cur.fetchall()
        return [{"id": r[0], "aluno": r[1], "plano": r[2], "inicio": r[3], "fim": r[4]} for r in rows]
    finally:
        cur.close()
        conn.close()


@router.get("/{id}", response_model=MatriculaResponse)
def buscar_matricula(id: int, current_user: str = Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT m.idmatricula, a.nomecliente, p.nomeplano, m.datainicio, m.datafim
            FROM matriculas m
            JOIN alunos a ON m.idaluno = a.idaluno
            JOIN planos p ON m.idplano = p.idplano
            WHERE m.idmatricula = %s
        """, (id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Matrícula não encontrada")
        return {"id": row[0], "aluno": row[1], "plano": row[2], "inicio": row[3], "fim": row[4]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()


@router.post("/", status_code=201)
def criar_matricula(matricula: MatriculaCreate, current_user: str = Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO matriculas (idaluno, idplano, idpersonal, datainicio, datafim)
            VALUES (%s, %s, %s, %s, %s) RETURNING idmatricula
        """, (matricula.idaluno, matricula.idplano, matricula.idpersonal,
              matricula.datainicio, matricula.datafim))
        novo_id = cur.fetchone()[0]
        conn.commit()
        return {"id": novo_id, **matricula.model_dump()}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()


@router.delete("/{id}", status_code=204)
def deletar_matricula(id: int, current_user: str = Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT idmatricula FROM matriculas WHERE idmatricula = %s", (id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Matrícula não encontrada")
        cur.execute("DELETE FROM matriculas WHERE idmatricula = %s", (id,))
        conn.commit()
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()