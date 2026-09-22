"""Тесты модуля управления задачами."""


def _register_and_login(client, username):
    """Регистрирует пользователя и возвращает его JWT-токен."""
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


def test_create_task(client):
    """Проверяет создание задачи менеджером."""
    token = _register_and_login(client, "manager1")

    response = client.post(
        "/tasks/",
        json={"title": "Test Task", "description": "Test Description"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"
    assert response.json()["status"] == "new"


def test_status_transition_valid(client):
    """Проверяет допустимый переход статуса new -> in_progress."""
    token = _register_and_login(client, "manager2")
    headers = {"Authorization": f"Bearer {token}"}

    task = client.post(
        "/tasks/",
        json={"title": "Task"},
        headers=headers,
    )
    task_id = task.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "in_progress"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_status_transition_invalid(client):
    """Проверяет запрещённый переход new -> done."""
    token = _register_and_login(client, "manager3")
    headers = {"Authorization": f"Bearer {token}"}

    # Сначала создаём задачу — без неё тест бессмысленен
    task = client.post(
        "/tasks/",
        json={"title": "Invalid transition task"},
        headers=headers,
    )
    task_id = task.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "done"},     # new -> done запрещено
        headers=headers,
    )
    assert response.status_code == 400


def test_integration_task_appears_in_report(client):
    """Интеграционный тест: задача, созданная пользователем, есть в отчёте."""
    token = _register_and_login(client, "integration_user")
    headers = {"Authorization": f"Bearer {token}"}

    task = client.post(
        "/tasks/",
        json={"title": "Integration Task"},
        headers=headers,
    )
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
