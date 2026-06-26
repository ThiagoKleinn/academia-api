from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from app.auth import verify_password, create_access_token, USERS_DB

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = USERS_DB.get(form_data.username)
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")
    token = create_access_token({"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}
