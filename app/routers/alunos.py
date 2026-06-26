from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from app.database import get_connection

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
def listar_alunos():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT idaluno, cpf, nomecliente FROM alunos ORDER BY idaluno")
        rows = cur.fetchall()
        return [{"id": r[0], "cpf": r[1], "nome": r[2]} for r in rows]
    finally:
        cur.close()
        conn.close()


@router.get("/{id}", response_model=AlunoResponse)
def buscar_aluno(id: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT idaluno, cpf, nomecliente FROM alunos WHERE idaluno = %s", (id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        return {"id": row[0], "cpf": row[1], "nome": row[2]}
    finally:
        cur.close()
        conn.close()


@router.post("/", response_model=AlunoResponse, status_code=201)
def criar_aluno(aluno: AlunoCreate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO alunos (cpf, nomecliente) VALUES (%s, %s) RETURNING idaluno",
            (aluno.cpf, aluno.nomecliente)
        )
        novo_id = cur.fetchone()[0]
        conn.commit()
        return {"id": novo_id, "cpf": aluno.cpf, "nome": aluno.nomecliente}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()


@router.put("/{id}", response_model=AlunoResponse)
def atualizar_aluno(id: int, aluno: AlunoCreate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT idaluno FROM alunos WHERE idaluno = %s", (id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        cur.execute(
            "UPDATE alunos SET cpf = %s, nomecliente = %s WHERE idaluno = %s",
            (aluno.cpf, aluno.nomecliente, id)
        )
        conn.commit()
        return {"id": id, "cpf": aluno.cpf, "nome": aluno.nomecliente}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()


@router.delete("/{id}", status_code=204)
def deletar_aluno(id: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT idaluno FROM alunos WHERE idaluno = %s", (id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        cur.execute("DELETE FROM alunos WHERE idaluno = %s", (id,))
        conn.commit()
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()