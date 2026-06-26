# app/routers/auth.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import verify_password, create_access_token, get_user

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = get_user(form_data.username, db)
    if not user or not verify_password(form_data.password, user[1]):
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")
    if not user[2]:  # ativo
        raise HTTPException(status_code=403, detail="Usuário inativo")
    token = create_access_token({"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}