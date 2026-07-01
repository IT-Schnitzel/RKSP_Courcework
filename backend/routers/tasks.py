from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from ..database import get_db
from .. import schemas, crud, auth, models

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

def get_current_user(session_id: str = Query(...)):
    user_id = auth.get_user_id_from_session(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return user_id

@router.get("/", response_model=List[schemas.TaskResponse])
def get_tasks(
    session_id: str = Query(...),
    skip: int = 0,
    limit: int = 100,
    status: Optional[models.TaskStatus] = None,
    priority: Optional[models.TaskPriority] = None,
    project_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    user_id = get_current_user(session_id)
    tasks = crud.get_tasks(db, user_id, skip, limit, status, priority, project_id, search)
    return tasks

@router.post("/", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: schemas.TaskCreate,
    session_id: str = Query(...),
    db: Session = Depends(get_db)
):
    user_id = get_current_user(session_id)
    assigned = crud.get_user_by_id(db, task.assigned_to_id)
    if not assigned:
        raise HTTPException(status_code=400, detail="Assigned user not found")
    return crud.create_task(db, task, user_id)

@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(
    task_id: int,
    session_id: str = Query(...),
    db: Session = Depends(get_db)
):
    user_id = get_current_user(session_id)
    task = crud.get_task(db, task_id, user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    session_id: str = Query(...),
    db: Session = Depends(get_db)
):
    user_id = get_current_user(session_id)
    task = crud.update_task(db, task_id, task_update, user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    session_id: str = Query(...),
    hard: bool = False,
    db: Session = Depends(get_db)
):
    user_id = get_current_user(session_id)
    deleted = crud.delete_task(db, task_id, user_id, hard)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}