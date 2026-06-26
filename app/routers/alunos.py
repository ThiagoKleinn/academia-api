# app/routers/alunos.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/alunos", tags=["Alunos"])


class AlunoCreate(BaseModel):
    cpf: str
    nomecliente: str

    @field_validator("cpf")
    def validar_cpf(cls, v):
        digits = "".join(filter(str.isdigit, v))
        if len(digits) != 11:
            raise ValueError("CPF deve ter 11 dígitos")
        return digits


class AlunoResponse(BaseModel):
    id: int
    cpf: str
    nome: str


@router.get("/", response_model=list[AlunoResponse])
def listar_alunos(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    offset = (page - 1) * limit
    rows = db.execute(
        text("SELECT idaluno, cpf, nomecliente FROM alunos ORDER BY idaluno LIMIT :limit OFFSET :offset"),
        {"limit": limit, "offset": offset}
    ).fetchall()
    return [{"id": r[0], "cpf": r[1], "nome": r[2]} for r in rows]


@router.get("/{id}", response_model=AlunoResponse)
def buscar_aluno(
    id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    row = db.execute(
        text("SELECT idaluno, cpf, nomecliente FROM alunos WHERE idaluno = :id"),
        {"id": id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return {"id": row[0], "cpf": row[1], "nome": row[2]}


@router.post("/", response_model=AlunoResponse, status_code=201)
def criar_aluno(
    aluno: AlunoCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        row = db.execute(
            text("INSERT INTO alunos (cpf, nomecliente) VALUES (:cpf, :nome) RETURNING idaluno"),
            {"cpf": aluno.cpf, "nome": aluno.nomecliente}
        ).fetchone()
        db.commit()
        return {"id": row[0], "cpf": aluno.cpf, "nome": aluno.nomecliente}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{id}", response_model=AlunoResponse)
def atualizar_aluno(
    id: int,
    aluno: AlunoCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    row = db.execute(
        text("SELECT idaluno FROM alunos WHERE idaluno = :id"),
        {"id": id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    try:
        db.execute(
            text("UPDATE alunos SET cpf = :cpf, nomecliente = :nome WHERE idaluno = :id"),
            {"cpf": aluno.cpf, "nome": aluno.nomecliente, "id": id}
        )
        db.commit()
        return {"id": id, "cpf": aluno.cpf, "nome": aluno.nomecliente}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{id}", status_code=204)
def deletar_aluno(
    id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    row = db.execute(
        text("SELECT idaluno FROM alunos WHERE idaluno = :id"),
        {"id": id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    try:
        db.execute(text("DELETE FROM alunos WHERE idaluno = :id"), {"id": id})
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))