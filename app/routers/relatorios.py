# relatorios.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import date
from typing import Optional
from app.database import get_connection
from app.auth import get_current_user

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])


class FaturamentoResponse(BaseModel):
    mes: str
    total_pagamentos: int
    receita_total: float


class InadimplenteResponse(BaseModel):
    idaluno: int
    aluno: str
    idmatricula: int
    plano: str
    vencimento: date


class PopularidadeResponse(BaseModel):
    plano: str
    total_matriculas: int
    receita_total: float


@router.get("/faturamento", response_model=list[FaturamentoResponse])
def faturamento_mensal(current_user: str = Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 
                TO_CHAR(datapagamento, 'YYYY-MM') AS mes,
                COUNT(*) AS total_pagamentos,
                SUM(valor) AS receita_total
            FROM pagamento
            GROUP BY TO_CHAR(datapagamento, 'YYYY-MM')
            ORDER BY mes
        """)
        rows = cur.fetchall()
        return [{"mes": r[0], "total_pagamentos": r[1], "receita_total": float(r[2])} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


@router.get("/inadimplentes", response_model=list[InadimplenteResponse])
def alunos_inadimplentes(current_user: str = Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 
                a.idaluno,
                a.nomecliente,
                m.idmatricula,
                p.nomeplano,
                m.datafim
            FROM matriculas m
            JOIN alunos a ON m.idaluno = a.idaluno
            JOIN planos p ON m.idplano = p.idplano
            LEFT JOIN pagamento pg ON pg.idmatricula = m.idmatricula
            WHERE m.datafim < CURRENT_DATE
            AND pg.idpagamento IS NULL
            ORDER BY m.datafim
        """)
        rows = cur.fetchall()
        return [{"idaluno": r[0], "aluno": r[1], "idmatricula": r[2], "plano": r[3], "vencimento": r[4]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


@router.get("/planos/popularidade", response_model=list[PopularidadeResponse])
def popularidade_planos(current_user: str = Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 
                p.nomeplano,
                COUNT(m.idmatricula) AS total_matriculas,
                SUM(pg.valor) AS receita_total
            FROM planos p
            LEFT JOIN matriculas m ON p.idplano = m.idplano
            LEFT JOIN pagamento pg ON m.idmatricula = pg.idmatricula
            GROUP BY p.nomeplano
            ORDER BY total_matriculas DESC
        """)
        rows = cur.fetchall()
        return [{"plano": r[0], "total_matriculas": r[1], "receita_total": float(r[2] or 0)} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()