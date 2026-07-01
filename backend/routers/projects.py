from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import schemas, crud, auth

router = APIRouter(prefix="/api/projects", tags=["projects"])

def get_current_user(session_id: str = Query(...)):
    user_id = auth.get_user_id_from_session(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return user_id

@router.get("/", response_model=List[schemas.ProjectResponse])
def get_projects(
    session_id: str = Query(...),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    get_current_user(session_id)
    return crud.get_projects(db, skip, limit)

@router.post("/", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project: schemas.ProjectCreate,
    session_id: str = Query(...),
    db: Session = Depends(get_db)
):
    user_id = get_current_user(session_id)
    return crud.create_project(db, project, user_id)

@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(
    project_id: int,
    session_id: str = Query(...),
    db: Session = Depends(get_db)
):
    get_current_user(session_id)
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=schemas.ProjectResponse)
def update_project(
    project_id: int,
    project_update: schemas.ProjectUpdate,
    session_id: str = Query(...),
    db: Session = Depends(get_db)
):
    user_id = get_current_user(session_id)
    project = crud.update_project(db, project_id, project_update, user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or no permission")
    return project

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    session_id: str = Query(...),
    hard: bool = False,
    db: Session = Depends(get_db)
):
    user_id = get_current_user(session_id)
    deleted = crud.delete_project(db, project_id, user_id, hard)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found or no permission")
    return {"message": "Project deleted"}