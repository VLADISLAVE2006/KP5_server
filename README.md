# Task Manager API

FastAPI-приложение для управления задачами с WebSocket-чатом.

## Структура проекта

```
app/
  main.py          — точка входа, WebSocket-маршруты
  dependencies.py  — зависимости FastAPI (авторизация, хранилище)
  schemas.py       — Pydantic-модели
  storage.py       — in-memory хранилище задач
  rooms.py         — RoomManager для WebSocket-комнат
  routers/
    tasks.py       — /tasks (CRUD задач)
    users.py       — /users
    admin.py       — /admin (статистика, удаление)
tests/
  conftest.py
  test_tasks.py
  test_websocket.py
  test_dependencies_and_routing.py
```

## Локальный запуск

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

API будет доступен по адресу: http://localhost:8000  
Документация: http://localhost:8000/docs

## Запуск тестов

```bash
pytest
```

## Запуск в Docker

```bash
docker compose up --build
```

API: http://localhost:8000

Проверка:
```bash
curl http://localhost:8000/tasks -H "X-User-Id: 10"
curl http://localhost:8000/health
```

## API

### Авторизация

Все `/tasks`, `/users`, `/admin` маршруты требуют заголовок `X-User-Id: <число>`.  
Маршруты `/admin` дополнительно требуют `X-User-Role: admin`.

### Маршруты

| Метод | Путь | Описание |
|-------|------|----------|
| POST | /tasks | Создать задачу |
| GET | /tasks | Список задач (фильтры: `status`, `min_priority`) |
| GET | /tasks/{id} | Получить задачу |
| PATCH | /tasks/{id}/status | Изменить статус |
| DELETE | /tasks/{id} | Удалить задачу |
| GET | /users/me | Текущий пользователь |
| GET | /users/{id} | Пользователь по ID |
| GET | /admin/stats | Статистика задач |
| DELETE | /admin/tasks/{id} | Удалить любую задачу |
| GET | /health | Состояние приложения |
| GET | /rooms/{room_id}/users | Активные пользователи комнаты |
| WS | /ws/rooms/{room_id}?username=X | WebSocket-чат |
