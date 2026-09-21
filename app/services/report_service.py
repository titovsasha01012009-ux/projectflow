"""Сервис генерации отчётов (PDF и Excel)."""
from io import BytesIO


def generate_pdf_report(tasks) -> BytesIO:
    """Генерация PDF-отчёта (заглушка)."""
    buffer = BytesIO()
    buffer.write(b"%PDF-1.4\n")
    buffer.write(b"% Report ProjectFlow\n")
    for t in tasks:
        line = f"Task #{t.id}: {t.title} [{t.status}]\n".encode("utf-8")
        buffer.write(line)
    buffer.seek(0)
    return buffer


def generate_excel_report(tasks) -> BytesIO:
    """Генерация Excel-отчёта (заглушка)."""
    buffer = BytesIO()
    buffer.write("ID,Title,Status,Assignee\n".encode("utf-8"))
    for t in tasks:
        line = f"{t.id},{t.title},{t.status},{t.assignee_id}\n".encode("utf-8")
        buffer.write(line)
    buffer.seek(0)
    return buffer
