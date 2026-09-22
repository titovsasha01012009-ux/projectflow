"""Тесты модуля отчётов."""


def _register_and_login(client, username):
    """Регистрирует менеджера и возвращает его JWT-токен."""
    client.post("/auth/register", json={
        "username": username,
        "email": f"{username}@example.com",
        "password": "secret123",
        "role": "manager",
    })
    login = client.post("/auth/login", data={
        "username": username,
        "password": "secret123",
    })
    return login.json()["access_token"]


def test_report_by_assignee(client):
    """Проверяет отчёт по конкретному исполнителю."""
    token = _register_and_login(client, "report_user1")
    headers = {"Authorization": f"Bearer {token}"}

    # Создаём задачу — она должна попасть в отчёт
    task = client.post(
        "/tasks/",
        json={"title": "Report task"},
        headers=headers,
    )
    assignee_id = task.json()["assignee_id"]

    response = client.get(
        f"/reports/tasks/by-assignee?assignee_id={assignee_id}",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["assignee_id"] == assignee_id
    assert data["count"] >= 1


def test_report_by_project(client):
    """Проверяет отчёт по проекту (пустой список — допустимо)."""
    token = _register_and_login(client, "report_user2")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(
        "/reports/tasks/by-project?project_id=999",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["project_id"] == 999
    assert response.json()["count"] == 0


def test_report_by_period(client):
    """Проверяет отчёт за период."""
    token = _register_and_login(client, "report_user3")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(
        "/reports/tasks/by-period?date_from=2020-01-01&date_to=2030-12-31",
        headers=headers,
    )
    assert response.status_code == 200
    assert "count" in response.json()


def test_export_pdf(client):
    """Проверяет экспорт отчёта в PDF."""
    token = _register_and_login(client, "report_user4")
    headers = {"Authorization": f"Bearer {token}"}

    task = client.post(
        "/tasks/",
        json={"title": "PDF task"},
        headers=headers,
    )
    task_id = task.json()["id"]

    response = client.get(
        f"/reports/export/pdf?task_ids={task_id}",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


def test_export_excel(client):
    """Проверяет экспорт отчёта в Excel."""
    token = _register_and_login(client, "report_user5")
    headers = {"Authorization": f"Bearer {token}"}

    task = client.post(
        "/tasks/",
        json={"title": "Excel task"},
        headers=headers,
    )
    task_id = task.json()["id"]

    response = client.get(
        f"/reports/export/excel?task_ids={task_id}",
        headers=headers,
    )
    assert response.status_code == 200


def test_integration_task_appears_in_report(client):
    """Интеграционный тест: создали задачу → она есть в отчёте."""
    token = _register_and_login(client, "report_integration")
    headers = {"Authorization": f"Bearer {token}"}

    task = client.post(
        "/tasks/",
        json={"title": "Integration Report Task"},
        headers=headers,
    )
    assert task.status_code == 200
    task_data = task.json()
    task_id = task_data["id"]
    assignee_id = task_data["assignee_id"]

    report = client.get(
        f"/reports/tasks/by-assignee?assignee_id={assignee_id}",
        headers=headers,
    )
    assert report.status_code == 200
    ids_in_report = [t["id"] for t in report.json()["tasks"]]
    assert task_id in ids_in_report
