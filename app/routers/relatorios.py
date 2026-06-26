# app/routers/relatorios.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import date
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
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
def faturamento_mensal(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        rows = db.execute(text("""
            SELECT
                TO_CHAR(datapagamento, 'YYYY-MM') AS mes,
                COUNT(*) AS total_pagamentos,
                SUM(valor) AS receita_total
            FROM pagamento
            GROUP BY TO_CHAR(datapagamento, 'YYYY-MM')
            ORDER BY mes
        """)).fetchall()
        return [{"mes": r[0], "total_pagamentos": r[1], "receita_total": float(r[2])} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inadimplentes", response_model=list[InadimplenteResponse])
def alunos_inadimplentes(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        rows = db.execute(text("""
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
        """)).fetchall()
        return [{"idaluno": r[0], "aluno": r[1], "idmatricula": r[2], "plano": r[3], "vencimento": r[4]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/planos/popularidade", response_model=list[PopularidadeResponse])
def popularidade_planos(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        rows = db.execute(text("""
            SELECT
                p.nomeplano,
                COUNT(m.idmatricula) AS total_matriculas,
                SUM(pg.valor) AS receita_total
            FROM planos p
            LEFT JOIN matriculas m ON p.idplano = m.idplano
            LEFT JOIN pagamento pg ON m.idmatricula = pg.idmatricula
            GROUP BY p.nomeplano
            ORDER BY total_matriculas DESC
        """)).fetchall()
        return [{"plano": r[0], "total_matriculas": r[1], "receita_total": float(r[2] or 0)} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))