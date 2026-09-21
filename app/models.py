"""Модели базы данных: users, projects, tasks, reports."""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """Пользователь системы (администратор, менеджер или исполнитель)."""

    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: str = Field(default="executor")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Project(SQLModel, table=True):
    """Проект, объединяющий задачи."""

    __tablename__ = "projects"    # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    owner_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Task(SQLModel, table=True):
    """Задача (документ) в рамках проекта."""

    __tablename__ = "tasks"     # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    status: str = Field(default="new")
    project_id: Optional[int] = Field(default=None, foreign_key="projects.id")
    assignee_id: Optional[int] = Field(default=None, foreign_key="users.id")
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Report(SQLModel, table=True):
    """Сформированный отчёт."""

    __tablename__ = "reports"   # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    report_type: str
    parameters: str
    created_by: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
