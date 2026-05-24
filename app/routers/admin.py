from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_storage, require_admin
from app.schemas import CurrentUser
from app.storage import TaskStorage

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def get_stats(
    _: CurrentUser = Depends(require_admin),
    store: TaskStorage = Depends(get_storage),
) -> dict:
    tasks = store.list_all()
    by_status: dict[str, int] = {}
    for task in tasks:
        by_status[task.status] = by_status.get(task.status, 0) + 1
    return {"total_tasks": len(tasks), "by_status": by_status}


@router.delete("/tasks/{task_id}", status_code=204)
def admin_delete_task(
    task_id: int,
    _: CurrentUser = Depends(require_admin),
    store: TaskStorage = Depends(get_storage),
) -> None:
    if not store.delete(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
