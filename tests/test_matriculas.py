# tests/test_matriculas.py
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_connection
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


def limpar_matriculas_teste():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            DELETE FROM matriculas 
            WHERE idaluno = %s AND idplano = %s
            AND datainicio = '2024-01-01'
        """, (ID_ALUNO_TESTE, ID_PLANO_TESTE))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def setup_function():
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
    assert response.status_code == 201
    assert response.json()["idaluno"] == ID_ALUNO_TESTE


def test_buscar_matricula():
    token = get_token()
    criado = client.post("/matriculas/", json={
        "idaluno": ID_ALUNO_TESTE,
        "idplano": ID_PLANO_TESTE,
        "datainicio": "2024-01-01",
        "datafim": "2024-02-01"
    }, headers={"Authorization": f"Bearer {token}"})
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
    id = criado.json()["id"]

    response = client.delete(f"/matriculas/{id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204

    response = client.get(f"/matriculas/{id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


def test_acesso_sem_token():
    response = client.get("/matriculas/")
    assert response.status_code == 401