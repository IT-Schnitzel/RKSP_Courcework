from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, crud, auth

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.post("/login", response_model=schemas.TokenResponse)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, login_data.username_or_email)
    if not user:
        user = crud.get_user_by_email(db, login_data.username_or_email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not auth.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    session_id = auth.create_session(user.id)
    return {"session_id": session_id, "user_id": user.id, "username": user.username}

@router.post("/logout")
def logout(session_id: str):
    auth.delete_session(session_id)
    return {"message": "Logged out"}