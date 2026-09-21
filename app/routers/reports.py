"""Эндпоинты формирования отчётов."""
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, col, select

from app.auth import get_current_user
from app.database import get_session
from app.models import Task, User
from app.services.report_service import (
    generate_excel_report,
    generate_pdf_report,
)

PDF_MEDIA_TYPE = "application/pdf"
XLSX_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

router = APIRouter(prefix="/reports", tags=["Отчёты"])


@router.get("/tasks/by-assignee")
def report_by_assignee(
    assignee_id: int,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    """Отчёт по задачам конкретного исполнителя."""
    tasks = session.exec(
        select(Task).where(col(Task.assignee_id) == assignee_id)
    ).all()
    return {
        "assignee_id": assignee_id,
        "count": len(tasks),
        "tasks": tasks,
    }


@router.get("/tasks/by-project")
def report_by_project(
    project_id: int,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    """Отчёт по задачам конкретного проекта."""
    tasks = session.exec(
        select(Task).where(col(Task.project_id) == project_id)
    ).all()
    return {
        "project_id": project_id,
        "count": len(tasks),
        "tasks": tasks,
    }


@router.get("/tasks/by-period")
def report_by_period(
    date_from: str,
    date_to: str,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    """Отчёт за период (формат дат YYYY-MM-DD)."""
    d1 = datetime.fromisoformat(date_from)
    d2 = datetime.fromisoformat(date_to)
    tasks = session.exec(
        select(Task).where(
            col(Task.created_at) >= d1, col(Task.created_at) <= d2
        )
    ).all()
    return {
        "from": date_from,
        "to": date_to,
        "count": len(tasks),
        "tasks": tasks,
    }


@router.get("/export/pdf")
def export_pdf(
    task_ids: str = Query(..., description="Список id через запятую"),
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    """Экспорт отчёта в PDF по списку id задач."""
    ids = [int(x) for x in task_ids.split(",")]
    tasks = session.exec(
        select(Task).where(col(Task.id).in_(ids))  # pylint: disable=no-member
    ).all()
    pdf_buffer = generate_pdf_report(tasks)
    return StreamingResponse(
        pdf_buffer,
        media_type=PDF_MEDIA_TYPE,
        headers={
            "Content-Disposition": "attachment; filename=report.pdf"
        },
    )


@router.get("/export/excel")
def export_excel(
    task_ids: str = Query(...),
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    """Экспорт отчёта в Excel по списку id задач."""
    ids = [int(x) for x in task_ids.split(",")]
    tasks = session.exec(
        select(Task).where(col(Task.id).in_(ids))  # pylint: disable=no-member
    ).all()
    buf = generate_excel_report(tasks)
    return StreamingResponse(
        buf,
        media_type=XLSX_MEDIA_TYPE,
        headers={
            "Content-Disposition": "attachment; filename=report.xlsx"
        },
    )
