from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlmodel import Session
from typing import List, Optional
import uuid
from app.database import get_session
from app.models.task import Task, TaskCreate, TaskUpdate
from app.services.task_service import TaskService
from app.auth.jwt_handler import get_current_user

router = APIRouter(tags=["tasks"])

@router.get("/api/{user_id}/tasks", response_model=List[Task])
async def list_tasks(
    user_id: str = Path(...),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = Query(None),
    sort_by: str = "created_at",
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    # Verify that the user_id in the URL matches the authenticated user
    if user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access forbidden: Cannot access other users' tasks")

    return TaskService.get_tasks(
        session,
        uuid.UUID(current_user["id"]),
        status,
        priority,
        search,
        sort_by
    )

@router.post("/api/{user_id}/tasks", response_model=Task, status_code=201)
async def create_task(
    user_id: str = Path(...),
    task: TaskCreate = None,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    # Verify that the user_id in the URL matches the authenticated user
    if user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access forbidden: Cannot create tasks for other users")

    return TaskService.create_task(session, task, uuid.UUID(current_user["id"]))

@router.get("/api/{user_id}/tasks/{task_id}", response_model=Task)
async def get_task(
    user_id: str = Path(...),
    task_id: uuid.UUID = Path(...),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    # Verify that the user_id in the URL matches the authenticated user
    if user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access forbidden: Cannot access other users' tasks")

    task = TaskService.get_task_by_id(session, task_id, uuid.UUID(current_user["id"]))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/api/{user_id}/tasks/{task_id}", response_model=Task)
async def update_task(
    user_id: str = Path(...),
    task_id: uuid.UUID = Path(...),
    task: TaskUpdate = None,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    # Verify that the user_id in the URL matches the authenticated user
    if user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access forbidden: Cannot update other users' tasks")

    db_task = TaskService.update_task(session, task_id, task, uuid.UUID(current_user["id"]))
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.patch("/api/{user_id}/tasks/{task_id}/complete", response_model=Task)
async def toggle_task_completion(
    user_id: str = Path(...),
    task_id: uuid.UUID = Path(...),
    completed: bool = None,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    # Verify that the user_id in the URL matches the authenticated user
    if user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access forbidden: Cannot update other users' tasks")

    task = TaskService.update_task_completion(session, task_id, completed, uuid.UUID(current_user["id"]))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/api/{user_id}/tasks/{task_id}", status_code=204)
async def delete_task(
    user_id: str = Path(...),
    task_id: uuid.UUID = Path(...),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    # Verify that the user_id in the URL matches the authenticated user
    if user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access forbidden: Cannot delete other users' tasks")

    success = TaskService.delete_task(session, task_id, uuid.UUID(current_user["id"]))
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return None
