"""Утилиты аутентификации: JWT-токены, хеширование паролей."""
from datetime import datetime, timedelta

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt


from sqlmodel import Session, col, select

from app.database import get_session
from app.models import User

SECRET_KEY = "change-me-in-production-please-use-env"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля его bcrypt-хешу."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_password_hash(password: str) -> str:
    """Возвращает bcrypt-хеш пароля."""
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def create_access_token(data: dict) -> str:
    """Создаёт JWT-токен с заданным payload и сроком жизни."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    """Достаёт пользователя из БД по JWT-токену из заголовка Authorization."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        raw_sub = payload.get("sub")
        if not isinstance(raw_sub, str):
            raise credentials_exception
        username: str = raw_sub
    except JWTError as exc:
        raise credentials_exception from exc

    statement = select(User).where(col(User.username) == username)
    user = session.exec(statement).first()
    if user is None:
        raise credentials_exception
    return user


def require_role(*roles: str):
    """Фабрика зависимостей для проверки роли пользователя."""

    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        """Проверяет, что роль пользователя входит в разрешённый список."""
        if current_user.role not in roles:
            raise HTTPException(
                status_code=403, detail="Insufficient permissions"
            )
        return current_user

    return role_checker  # noqa: R1710
