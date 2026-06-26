"""
Script de seed para criar (ou atualizar) o usuário admin do sistema.

Uso:
    python seed.py

Lê as credenciais de ADMIN_USERNAME / ADMIN_PASSWORD no .env
(mesmas variáveis já usadas nos testes) e gera o hash bcrypt
correto usando a mesma função de hash da aplicação (app/auth.py) —
evitando o problema de hash divergente que já causou bug no projeto.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import text

from app.database import SessionLocal
from app.auth import hash_password

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


def seed_admin():
    db = SessionLocal()
    try:
        hashed_password = hash_password(ADMIN_PASSWORD)

        existing = db.execute(
            text("SELECT idusuario FROM usuarios WHERE username = :username"),
            {"username": ADMIN_USERNAME}
        ).fetchone()

        if existing:
            db.execute(
                text("UPDATE usuarios SET password = :password, ativo = true WHERE username = :username"),
                {"password": hashed_password, "username": ADMIN_USERNAME}
            )
            print(f"Usuário '{ADMIN_USERNAME}' já existia — senha atualizada.")
        else:
            db.execute(
                text("INSERT INTO usuarios (username, password, ativo) VALUES (:username, :password, true)"),
                {"username": ADMIN_USERNAME, "password": hashed_password}
            )
            print(f"Usuário '{ADMIN_USERNAME}' criado com sucesso.")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()