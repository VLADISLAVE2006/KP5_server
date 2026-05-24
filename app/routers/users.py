from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_current_user, get_storage
from app.schemas import CurrentUser
from app.storage import TaskStorage

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_me(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return user


@router.get("/{user_id}")
def get_user(
    user_id: int,
    store: TaskStorage = Depends(get_storage),
    _: CurrentUser = Depends(get_current_user),
) -> dict:
    tasks = store.list_by_owner(user_id)
    return {"id": user_id, "task_count": len(tasks)}
