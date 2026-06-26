# app/routers/pagamentos.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, field_validator
from datetime import date
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])


class PagamentoCreate(BaseModel):
    idmatricula: int
    valor: float
    datapagamento: date
    formadepagamento: str
    funcionariopago: int

    @field_validator("valor")
    def validar_valor(cls, v):
        if v <= 0:
            raise ValueError("Valor deve ser maior que zero")
        return v

    @field_validator("formadepagamento")
    def validar_forma(cls, v):
        formas_validas = {"dinheiro", "cartao_credito", "cartao_debito", "pix"}
        if v.lower() not in formas_validas:
            raise ValueError(f"Forma de pagamento inválida. Use: {formas_validas}")
        return v.lower()


class PagamentoResponse(BaseModel):
    id: int
    aluno: str
    valor: float
    data: date
    forma: str


@router.get("/", response_model=list[PagamentoResponse])
def listar_pagamentos(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    offset = (page - 1) * limit
    rows = db.execute(text("""
        SELECT p.idpagamento, a.nomecliente, p.valor, p.datapagamento, p.formadepagamento
        FROM pagamento p
        JOIN matriculas m ON p.idmatricula = m.idmatricula
        JOIN alunos a ON m.idaluno = a.idaluno
        ORDER BY p.idpagamento
        LIMIT :limit OFFSET :offset
    """), {"limit": limit, "offset": offset}).fetchall()
    return [{"id": r[0], "aluno": r[1], "valor": r[2], "data": r[3], "forma": r[4]} for r in rows]


@router.get("/{id}", response_model=PagamentoResponse)
def buscar_pagamento(
    id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    row = db.execute(text("""
        SELECT p.idpagamento, a.nomecliente, p.valor, p.datapagamento, p.formadepagamento
        FROM pagamento p
        JOIN matriculas m ON p.idmatricula = m.idmatricula
        JOIN alunos a ON m.idaluno = a.idaluno
        WHERE p.idpagamento = :id
    """), {"id": id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return {"id": row[0], "aluno": row[1], "valor": row[2], "data": row[3], "forma": row[4]}


@router.post("/", status_code=201)
def criar_pagamento(
    pagamento: PagamentoCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        row = db.execute(text("""
            INSERT INTO pagamento (idmatricula, valor, datapagamento, formadepagamento, funcionariopago)
            VALUES (:idmatricula, :valor, :datapagamento, :formadepagamento, :funcionariopago)
            RETURNING idpagamento
        """), pagamento.model_dump()).fetchone()
        db.commit()
        return {"id": row[0], **pagamento.model_dump()}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))