from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import text
from app.database import get_db
import os

client = TestClient(app)

ID_ALUNO_TESTE = 1
ID_PLANO_TESTE = 1


def get_token():
    response = client.post("/auth/login", data={
        "username": os.getenv("ADMIN_USERNAME", "admin"),
        "password": os.getenv("ADMIN_PASSWORD", "admin123")
    })
    return response.json()["access_token"]


def garantir_aluno_e_plano_teste():
    """Garante que o aluno e o plano usados nos testes de matrícula existem,
    independente do estado do banco (necessário em CI, que começa com banco vazio)."""
    db = next(get_db())
    try:
        aluno = db.execute(
            text("SELECT idaluno FROM alunos WHERE idaluno = :id"),
            {"id": ID_ALUNO_TESTE}
        ).fetchone()
        if not aluno:
            db.execute(text("""
                INSERT INTO alunos (idaluno, cpf, nomecliente)
                VALUES (:id, '00000000000', 'Aluno Teste Matricula')
            """), {"id": ID_ALUNO_TESTE})

        plano = db.execute(
            text("SELECT idplano FROM planos WHERE idplano = :id"),
            {"id": ID_PLANO_TESTE}
        ).fetchone()
        if not plano:
            db.execute(text("""
                INSERT INTO planos (idplano, nomeplano, valorplano, duracao)
                VALUES (:id, 'Plano Teste', 99.90, 1)
            """), {"id": ID_PLANO_TESTE})

        db.commit()
    finally:
        db.close()


def limpar_matriculas_teste():
    db = next(get_db())
    try:
        db.execute(text("DELETE FROM matriculas WHERE idaluno = :id AND idplano = :plano AND datainicio = '2024-01-01'"),
                   {"id": ID_ALUNO_TESTE, "plano": ID_PLANO_TESTE})
        db.commit()
    finally:
        db.close()


def setup_function():
    garantir_aluno_e_plano_teste()
    limpar_matriculas_teste()


def test_listar_matriculas():
    token = get_token()
    response = client.get("/matriculas/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_criar_matricula():
    token = get_token()
    response = client.post("/matriculas/", json={
        "idaluno": ID_ALUNO_TESTE,
        "idplano": ID_PLANO_TESTE,
        "datainicio": "2024-01-01",
        "datafim": "2024-02-01"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201, response.text
    assert response.json()["idaluno"] == ID_ALUNO_TESTE


def test_buscar_matricula():
    token = get_token()
    criado = client.post("/matriculas/", json={
        "idaluno": ID_ALUNO_TESTE,
        "idplano": ID_PLANO_TESTE,
        "datainicio": "2024-01-01",
        "datafim": "2024-02-01"
    }, headers={"Authorization": f"Bearer {token}"})
    assert criado.status_code == 201, criado.text
    id = criado.json()["id"]

    response = client.get(f"/matriculas/{id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == id


def test_buscar_matricula_inexistente():
    token = get_token()
    response = client.get("/matriculas/999999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


def test_deletar_matricula():
    token = get_token()
    criado = client.post("/matriculas/", json={
        "idaluno": ID_ALUNO_TESTE,
        "idplano": ID_PLANO_TESTE,
        "datainicio": "2024-01-01",
        "datafim": "2024-02-01"
    }, headers={"Authorization": f"Bearer {token}"})
    assert criado.status_code == 201, criado.text
    id = criado.json()["id"]

    response = client.delete(f"/matriculas/{id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204

    response = client.get(f"/matriculas/{id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


def test_acesso_sem_token():
    response = client.get("/matriculas/")
    assert response.status_code == 401