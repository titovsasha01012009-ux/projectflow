"""Точка входа приложения ProjectFlow."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import auth, reports, tasks


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Создаёт таблицы БД при старте приложения."""
    create_db_and_tables()
    yield


app = FastAPI(
    title="ProjectFlow API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(reports.router)


@app.get("/")
def root():
    """Корневой эндпоинт — проверка работоспособности API."""
    return {"message": "ProjectFlow API", "docs": "/docs"}
