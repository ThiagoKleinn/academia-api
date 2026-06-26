# tests/test_relatorios.py
from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)


def get_token():
    response = client.post("/auth/login", data={
        "username": os.getenv("ADMIN_USERNAME", "admin"),
        "password": os.getenv("ADMIN_PASSWORD", "admin123")
    })
    return response.json()["access_token"]


def test_faturamento_mensal():
    token = get_token()
    response = client.get("/relatorios/faturamento", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for item in response.json():
        assert "mes" in item
        assert "total_pagamentos" in item
        assert "receita_total" in item


def test_inadimplentes():
    token = get_token()
    response = client.get("/relatorios/inadimplentes", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for item in response.json():
        assert "idaluno" in item
        assert "aluno" in item
        assert "vencimento" in item


def test_popularidade_planos():
    token = get_token()
    response = client.get("/relatorios/planos/popularidade", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for item in response.json():
        assert "plano" in item
        assert "total_matriculas" in item
        assert "receita_total" in item


def test_faturamento_sem_token():
    response = client.get("/relatorios/faturamento")
    assert response.status_code == 401


def test_inadimplentes_sem_token():
    response = client.get("/relatorios/inadimplentes")
    assert response.status_code == 401


def test_popularidade_sem_token():
    response = client.get("/relatorios/planos/popularidade")
    assert response.status_code == 401