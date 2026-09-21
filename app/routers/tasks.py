"""Эндпоинты управления задачами (документами проекта)."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, col, select

from app.auth import get_current_user, require_role
from app.database import get_session
from app.models import Task, User
from app.schemas import TaskCreate, TaskStatusUpdate

router = APIRouter(prefix="/tasks", tags=["Управление документами"])

# Матрица допустимых переходов статусов задачи
# (соответствует диаграмме состояний, см. docs/state_diagram.drawio)
VALID_TRANSITIONS = {
    "new": ["in_progress", "rejected"],
    "in_progress": ["review", "rejected"],
    "review": ["done", "rejected"],
    "rejected": ["new"],
    "done": [],
}


@router.post("/", response_model=Task)
def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("admin", "manager")),
):
    """Создать новую задачу. Доступ: admin или manager."""
    task = Task(**task_data.model_dump(), assignee_id=current_user.id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/", response_model=List[Task])
def list_tasks(
    status: Optional[str] = None,
    assignee_id: Optional[int] = None,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    """Получить список задач с опциональными фильтрами."""
    query = select(Task)
    if status:
        query = query.where(col(Task.status) == status)
    if assignee_id:
        query = query.where(col(Task.assignee_id) == assignee_id)
    return session.exec(query).all()


@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    """Получить задачу по её идентификатору."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/status", response_model=Task)
def update_status(
    task_id: int,
    status_data: TaskStatusUpdate,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    """Изменить статус задачи с проверкой допустимости перехода."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    allowed = VALID_TRANSITIONS.get(task.status, [])
    if status_data.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid transition from "
                f"{task.status} to {status_data.status}"
            ),
        )

    task.status = status_data.status
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    _current_user: User = Depends(require_role("admin", "manager")),
):
    """Удалить задачу. Доступ: admin или manager."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}
