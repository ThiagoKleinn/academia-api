# app/routers/matriculas.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import date
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
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
def listar_matriculas(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    offset = (page - 1) * limit
    rows = db.execute(text("""
        SELECT m.idmatricula, a.nomecliente, p.nomeplano, m.datainicio, m.datafim
        FROM matriculas m
        JOIN alunos a ON m.idaluno = a.idaluno
        JOIN planos p ON m.idplano = p.idplano
        ORDER BY m.idmatricula
        LIMIT :limit OFFSET :offset
    """), {"limit": limit, "offset": offset}).fetchall()
    return [{"id": r[0], "aluno": r[1], "plano": r[2], "inicio": r[3], "fim": r[4]} for r in rows]


@router.get("/{id}", response_model=MatriculaResponse)
def buscar_matricula(
    id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    row = db.execute(text("""
        SELECT m.idmatricula, a.nomecliente, p.nomeplano, m.datainicio, m.datafim
        FROM matriculas m
        JOIN alunos a ON m.idaluno = a.idaluno
        JOIN planos p ON m.idplano = p.idplano
        WHERE m.idmatricula = :id
    """), {"id": id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")
    return {"id": row[0], "aluno": row[1], "plano": row[2], "inicio": row[3], "fim": row[4]}


@router.post("/", status_code=201)
def criar_matricula(
    matricula: MatriculaCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        row = db.execute(text("""
            INSERT INTO matriculas (idaluno, idplano, idpersonal, datainicio, datafim)
            VALUES (:idaluno, :idplano, :idpersonal, :datainicio, :datafim)
            RETURNING idmatricula
        """), matricula.model_dump()).fetchone()
        db.commit()
        return {"id": row[0], **matricula.model_dump()}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{id}", status_code=204)
def deletar_matricula(
    id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    row = db.execute(
        text("SELECT idmatricula FROM matriculas WHERE idmatricula = :id"),
        {"id": id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")
    try:
        db.execute(text("DELETE FROM matriculas WHERE idmatricula = :id"), {"id": id})
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))