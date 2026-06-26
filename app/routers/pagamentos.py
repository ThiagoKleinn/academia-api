from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
from app.database import get_connection

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])

class PagamentoCreate(BaseModel):
    idmatricula: int
    valor: float
    datapagamento: date
    formadepagamento: str
    funcionariopago: int

@router.get("/")
def listar_pagamentos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.idpagamento, a.nomecliente, p.valor, p.datapagamento, p.formadepagamento
        FROM pagamento p
        JOIN matriculas m ON p.idmatricula = m.idmatricula
        JOIN alunos a ON m.idaluno = a.idaluno
        ORDER BY p.idpagamento
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "aluno": r[1], "valor": r[2], "data": r[3], "forma": r[4]} for r in rows]

@router.get("/{id}")
def buscar_pagamento(id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.idpagamento, a.nomecliente, p.valor, p.datapagamento, p.formadepagamento
        FROM pagamento p
        JOIN matriculas m ON p.idmatricula = m.idmatricula
        JOIN alunos a ON m.idaluno = a.idaluno
        WHERE p.idpagamento = %s
    """, (id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return {"id": row[0], "aluno": row[1], "valor": row[2], "data": row[3], "forma": row[4]}

@router.post("/", status_code=201)
def criar_pagamento(pagamento: PagamentoCreate):
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
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"id": novo_id, **pagamento.dict()}