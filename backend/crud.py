from sqlalchemy.orm import Session
from . import models, schemas, auth
from datetime import datetime, timezone
from typing import Optional, List


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    # Очистка от null-символов
    clean_username = user.username.replace('\u0000', '').strip()
    if not clean_username:
        raise ValueError("Username cannot be empty after cleaning")

    hashed = auth.get_password_hash(user.password)
    db_user = models.User(
        username=clean_username,
        email=user.email,
        hashed_password=hashed,
        full_name=user.full_name,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_task(db: Session, task: schemas.TaskCreate, user_id: int) -> models.Task:
    db_task = models.Task(
        **task.dict(),
        created_by_id=user_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task(db: Session, task_id: int, user_id: int) -> models.Task:
    return db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.is_active == True,
        (models.Task.assigned_to_id == user_id) | (models.Task.created_by_id == user_id)
    ).first()


def get_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100,
              status: Optional[models.TaskStatus] = None,
              priority: Optional[models.TaskPriority] = None,
              project_id: Optional[int] = None,
              search: Optional[str] = None) -> List[models.Task]:
    query = db.query(models.Task).filter(
        models.Task.is_active == True,
        (models.Task.assigned_to_id == user_id) | (models.Task.created_by_id == user_id)
    )
    if status:
        query = query.filter(models.Task.status == status)
    if priority:
        query = query.filter(models.Task.priority == priority)
    if project_id:
        query = query.filter(models.Task.project_id == project_id)
    if search:
        query = query.filter(
            (models.Task.title.ilike(f"%{search}%")) |
            (models.Task.description.ilike(f"%{search}%"))
        )
    return query.offset(skip).limit(limit).all()


def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate, user_id: int) -> models.Task:
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return None
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    if 'status' in update_data and update_data['status'] == models.TaskStatus.COMPLETED:
        db_task.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int, user_id: int, hard_delete: bool = False) -> bool:
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return False
    if hard_delete:
        db.delete(db_task)
    else:
        db_task.is_active = False
    db.commit()
    return True


def create_project(db: Session, project: schemas.ProjectCreate, user_id: int) -> models.Project:
    db_project = models.Project(
        **project.dict(),
        owner_id=user_id,
        is_public=True
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_project(db: Session, project_id: int) -> models.Project:
    return db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.is_active == True
    ).first()


def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[models.Project]:
    return db.query(models.Project).filter(
        models.Project.is_active == True
    ).offset(skip).limit(limit).all()


def update_project(db: Session, project_id: int, project_update: schemas.ProjectUpdate, user_id: int) -> models.Project:
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    if db_project.owner_id != user_id:
        return None
    update_data = project_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, project_id: int, user_id: int, hard_delete: bool = False) -> bool:
    db_project = get_project(db, project_id)
    if not db_project:
        return False
    if db_project.owner_id != user_id:
        return False
    if hard_delete:
        db.delete(db_project)
    else:
        db_project.is_active = False
    db.commit()
    return True


def get_stats_overview(db: Session, user_id: int) -> dict:
    tasks = db.query(models.Task).filter(
        models.Task.is_active == True,
        (models.Task.assigned_to_id == user_id) | (models.Task.created_by_id == user_id)
    ).all()
    total = len(tasks)
    completed = sum(1 for t in tasks if t.status == models.TaskStatus.COMPLETED)
    now = datetime.now(timezone.utc)
    overdue = sum(1 for t in tasks if t.deadline and t.deadline < now and t.status != models.TaskStatus.COMPLETED)
    status_dist = {}
    priority_dist = {}
    workload = {}
    for t in tasks:
        status_dist[t.status.value] = status_dist.get(t.status.value, 0) + 1
        priority_dist[t.priority.value] = priority_dist.get(t.priority.value, 0) + 1
        if t.assigned_to_id:
            if t.assigned_to_id not in workload:
                workload[t.assigned_to_id] = {'planned': 0, 'actual': 0, 'count': 0}
            workload[t.assigned_to_id]['planned'] += t.planned_hours or 0
            workload[t.assigned_to_id]['actual'] += t.actual_hours or 0
            workload[t.assigned_to_id]['count'] += 1
    user_ids = list(workload.keys())
    users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()
    user_map = {u.id: u.username for u in users}
    workload_list = []
    for uid, data in workload.items():
        workload_list.append({
            'user_id': uid,
            'username': user_map.get(uid, 'Unknown'),
            'planned_hours': data['planned'],
            'actual_hours': data['actual'],
            'task_count': data['count']
        })
    return {
        'total_tasks': total,
        'status_distribution': [{'status': k, 'count': v} for k, v in status_dist.items()],
        'priority_distribution': [{'priority': k, 'count': v} for k, v in priority_dist.items()],
        'user_workload': workload_list,
        'overdue_tasks': overdue,
        'completed_tasks': completed,
        'completion_rate': (completed / total * 100) if total > 0 else 0
    }