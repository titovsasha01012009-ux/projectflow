"""Эндпоинты авторизации: регистрация и вход."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, col, select

from app.auth import create_access_token, get_password_hash, verify_password
from app.database import get_session
from app.models import User
from app.schemas import Token, UserCreate

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/register", response_model=User)
def register(
    user_data: UserCreate,
    session: Session = Depends(get_session),
):
    """Регистрация нового пользователя."""
    existing = session.exec(
        select(User).where(col(User.username) == user_data.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """Аутентификация пользователя и выдача JWT-токена."""
    user = session.exec(
        select(User).where(col(User.username) == form_data.username)
    ).first()

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    return Token(access_token=token, token_type="bearer")
