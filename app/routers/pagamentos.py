# pagamentos.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, field_validator
from datetime import date
from app.database import get_connection
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
def listar_pagamentos(current_user: str = Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT p.idpagamento, a.nomecliente, p.valor, p.datapagamento, p.formadepagamento
            FROM pagamento p
            JOIN matriculas m ON p.idmatricula = m.idmatricula
            JOIN alunos a ON m.idaluno = a.idaluno
            ORDER BY p.idpagamento
        """)
        rows = cur.fetchall()
        return [{"id": r[0], "aluno": r[1], "valor": r[2], "data": r[3], "forma": r[4]} for r in rows]
    finally:
        cur.close()
        conn.close()


@router.get("/{id}", response_model=PagamentoResponse)
def buscar_pagamento(id: int, current_user: str = Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT p.idpagamento, a.nomecliente, p.valor, p.datapagamento, p.formadepagamento
            FROM pagamento p
            JOIN matriculas m ON p.idmatricula = m.idmatricula
            JOIN alunos a ON m.idaluno = a.idaluno
            WHERE p.idpagamento = %s
        """, (id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Pagamento não encontrado")
        return {"id": row[0], "aluno": row[1], "valor": row[2], "data": row[3], "forma": row[4]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()


@router.post("/", status_code=201)
def criar_pagamento(pagamento: PagamentoCreate, current_user: str = Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO pagamento (idmatricula, valor, datapagamento, formadepagamento, funcionariopago)
            VALUES (%s, %s, %s, %s, %s) RETURNING idpagamento
        """, (pagamento.idmatricula, pagamento.valor, pagamento.datapagamento,
              pagamento.formadepagamento, pagamento.funcionariopago))
        novo_id = cur.fetchone()[0]
        conn.commit()
        return {"id": novo_id, **pagamento.model_dump()}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()