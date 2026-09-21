"""Подключение к базе данных SQLite через SQLModel."""
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./projectflow.db"
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    """Генератор сессий для внедрения зависимостей FastAPI."""
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    """Создаёт все таблицы при старте приложения."""
    SQLModel.metadata.create_all(engine)
