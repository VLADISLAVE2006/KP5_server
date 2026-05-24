from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_current_user, get_storage
from app.schemas import CurrentUser, TaskCreate, TaskResponse, TaskStatusUpdate
from app.storage import TaskStorage

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    body: TaskCreate,
    user: CurrentUser = Depends(get_current_user),
    store: TaskStorage = Depends(get_storage),
) -> TaskResponse:
    return store.create(
        title=body.title,
        description=body.description,
        status=body.status,
        priority=body.priority,
        owner_id=user.id,
    )


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    status: str | None = None,
    min_priority: int | None = None,
    user: CurrentUser = Depends(get_current_user),
    store: TaskStorage = Depends(get_storage),
) -> list[TaskResponse]:
    return store.list_by_owner(user.id, status=status, min_priority=min_priority)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    user: CurrentUser = Depends(get_current_user),
    store: TaskStorage = Depends(get_storage),
) -> TaskResponse:
    task = store.get(task_id)
    if task is None or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    body: TaskStatusUpdate,
    user: CurrentUser = Depends(get_current_user),
    store: TaskStorage = Depends(get_storage),
) -> TaskResponse:
    task = store.get(task_id)
    if task is None or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return store.update_status(task_id, body.status)


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    user: CurrentUser = Depends(get_current_user),
    store: TaskStorage = Depends(get_storage),
) -> None:
    task = store.get(task_id)
    if task is None or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    store.delete(task_id)
