from app.schemas import TaskResponse


class TaskStorage:
    def __init__(self) -> None:
        self._tasks: dict[int, TaskResponse] = {}
        self._next_id: int = 1

    def create(self, title: str, description: str | None, status: str, priority: int, owner_id: int) -> TaskResponse:
        task = TaskResponse(
            id=self._next_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            owner_id=owner_id,
        )
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get(self, task_id: int) -> TaskResponse | None:
        return self._tasks.get(task_id)

    def list_by_owner(self, owner_id: int, status: str | None = None, min_priority: int | None = None) -> list[TaskResponse]:
        result = [t for t in self._tasks.values() if t.owner_id == owner_id]
        if status is not None:
            result = [t for t in result if t.status == status]
        if min_priority is not None:
            result = [t for t in result if t.priority >= min_priority]
        return result

    def list_all(self) -> list[TaskResponse]:
        return list(self._tasks.values())

    def update_status(self, task_id: int, new_status: str) -> TaskResponse | None:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        self._tasks[task_id] = task.model_copy(update={"status": new_status})
        return self._tasks[task_id]

    def delete(self, task_id: int) -> bool:
        if task_id not in self._tasks:
            return False
        del self._tasks[task_id]
        return True

    def clear(self) -> None:
        self._tasks.clear()
        self._next_id = 1


storage = TaskStorage()
