from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import text
from app.database import get_db
import os

client = TestClient(app)

def get_token():
    response = client.post("/auth/login", data={
        "username": os.getenv("ADMIN_USERNAME", "admin"),
        "password": os.getenv("ADMIN_PASSWORD", "admin123")
    })
    return response.json()["access_token"]

def get_idmatricula():
    db = next(get_db())
    try:
        row = db.execute(text("SELECT idmatricula FROM matriculas LIMIT 1")).fetchone()
        return row[0] if row else None
    finally:
        db.close()

def limpar_pagamentos_teste(idmatricula):
    db = next(get_db())
    try:
        db.execute(text("DELETE FROM pagamento WHERE idmatricula = :id AND valor = 99.99"), {"id": idmatricula})
        db.commit()
    finally:
        db.close()

def setup_function():
    idmatricula = get_idmatricula()
    if idmatricula:
        limpar_pagamentos_teste(idmatricula)


def test_listar_pagamentos():
    token = get_token()
    response = client.get("/pagamentos/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_criar_pagamento():
    token = get_token()
    idmatricula = get_idmatricula()
    response = client.post("/pagamentos/", json={
        "idmatricula": idmatricula,
        "valor": 99.99,
        "datapagamento": "2024-01-01",
        "formadepagamento": "pix",
        "funcionariopago": 1
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.json()["valor"] == 99.99


def test_buscar_pagamento():
    token = get_token()
    idmatricula = get_idmatricula()
    criado = client.post("/pagamentos/", json={
        "idmatricula": idmatricula,
        "valor": 99.99,
        "datapagamento": "2024-01-01",
        "formadepagamento": "pix",
        "funcionariopago": 1
    }, headers={"Authorization": f"Bearer {token}"})
    id = criado.json()["id"]

    response = client.get(f"/pagamentos/{id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == id


def test_buscar_pagamento_inexistente():
    token = get_token()
    response = client.get("/pagamentos/999999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


def test_forma_pagamento_invalida():
    token = get_token()
    idmatricula = get_idmatricula()
    response = client.post("/pagamentos/", json={
        "idmatricula": idmatricula,
        "valor": 99.99,
        "datapagamento": "2024-01-01",
        "formadepagamento": "cheque",
        "funcionariopago": 1
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422


def test_valor_invalido():
    token = get_token()
    idmatricula = get_idmatricula()
    response = client.post("/pagamentos/", json={
        "idmatricula": idmatricula,
        "valor": -50.0,
        "datapagamento": "2024-01-01",
        "formadepagamento": "pix",
        "funcionariopago": 1
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422


def test_acesso_sem_token():
    response = client.get("/pagamentos/")
    assert response.status_code == 401