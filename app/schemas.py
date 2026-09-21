"""Pydantic-схемы для валидации входящих данных."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    """Данные для регистрации пользователя."""

    username: str
    email: str
    password: str
    role: str = "executor"


class UserRead(BaseModel):
    """Публичное представление пользователя."""

    id: int
    username: str
    email: str
    role: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Ответ при успешном логине."""

    access_token: str
    token_type: str


class TaskCreate(BaseModel):
    """Данные для создания задачи."""

    title: str
    description: Optional[str] = None
    project_id: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    """Данные для обновления задачи."""

    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskStatusUpdate(BaseModel):
    """Данные для смены статуса задачи."""

    status: str
