from fastapi.testclient import TestClient
from app.main import app
from app.database import get_connection
import os

client = TestClient(app)

def get_token():
    response = client.post("/auth/login", data={
        "username": os.getenv("ADMIN_USERNAME", "admin"),
        "password": os.getenv("ADMIN_PASSWORD", "admin123")
    })
    return response.json()["access_token"]

def limpar_alunos_teste():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM alunos WHERE cpf IN ('12345678901','98765432100','11122233344','55566677788')")
        conn.commit()
    finally:
        cur.close()
        conn.close()

def setup_function():
    limpar_alunos_teste()

def test_listar_alunos():
    token = get_token()
    response = client.get("/alunos/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_criar_aluno():
    token = get_token()
    response = client.post("/alunos/", json={
        "cpf": "12345678901",
        "nomecliente": "Aluno Teste"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.json()["nome"] == "Aluno Teste"
    assert response.json()["cpf"] == "12345678901"

def test_buscar_aluno():
    token = get_token()
    criado = client.post("/alunos/", json={
        "cpf": "98765432100",
        "nomecliente": "Aluno Busca"
    }, headers={"Authorization": f"Bearer {token}"})
    id = criado.json()["id"]
    response = client.get(f"/alunos/{id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == id

def test_buscar_aluno_inexistente():
    token = get_token()
    response = client.get("/alunos/999999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404

def test_atualizar_aluno():
    token = get_token()
    criado = client.post("/alunos/", json={
        "cpf": "11122233344",
        "nomecliente": "Aluno Original"
    }, headers={"Authorization": f"Bearer {token}"})
    id = criado.json()["id"]
    response = client.put(f"/alunos/{id}", json={
        "cpf": "11122233344",
        "nomecliente": "Aluno Atualizado"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["nome"] == "Aluno Atualizado"

def test_deletar_aluno():
    token = get_token()
    criado = client.post("/alunos/", json={
        "cpf": "55566677788",
        "nomecliente": "Aluno Delete"
    }, headers={"Authorization": f"Bearer {token}"})
    id = criado.json()["id"]
    response = client.delete(f"/alunos/{id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204
    response = client.get(f"/alunos/{id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404

def test_cpf_invalido():
    token = get_token()
    response = client.post("/alunos/", json={
        "cpf": "123",
        "nomecliente": "CPF Inválido"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422

def test_acesso_sem_token():
    response = client.get("/alunos/")
    assert response.status_code == 401