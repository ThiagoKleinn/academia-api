from fastapi import APIRouter
from app.database import get_connection

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])

@router.get("/faturamento")
def faturamento_mensal():
    conn = get_connection()
    cur = conn.cursor()
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
    cur.close()
    conn.close()
    return [{"mes": r[0], "total_pagamentos": r[1], "receita_total": float(r[2])} for r in rows]

@router.get("/inadimplentes")
def alunos_inadimplentes():
    conn = get_connection()
    cur = conn.cursor()
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
    cur.close()
    conn.close()
    return [{"idaluno": r[0], "aluno": r[1], "idmatricula": r[2], "plano": r[3], "vencimento": r[4]} for r in rows]

@router.get("/planos/popularidade")
def popularidade_planos():
    conn = get_connection()
    cur = conn.cursor()
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
    cur.close()
    conn.close()
    return [{"plano": r[0], "total_matriculas": r[1], "receita_total": float(r[2] or 0)} for r in rows]