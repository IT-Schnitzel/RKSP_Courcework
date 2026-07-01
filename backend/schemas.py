from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from .models import TaskStatus, TaskPriority, UserRole, ProjectStatus


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.EXECUTOR

    @validator('username')
    def validate_username(cls, v):
        v = v.replace('\u0000', '').strip()
        if not v:
            raise ValueError('Username cannot be empty')
        return v

    @validator('email')
    def validate_email(cls, v):
        # Разрешаем только домены .com и .ru
        allowed_domains = ['.com', '.ru']
        if not any(v.endswith(domain) for domain in allowed_domains):
            raise ValueError(f'Email must use one of the following domains: {", ".join(allowed_domains)}')

        # Проверяем, что в домене есть минимум 2 символа после точки
        if '.' in v:
            domain_part = v.split('@')[1] if '@' in v else ''
            if '.' in domain_part:
                tld = domain_part.split('.')[-1]
                if len(tld) < 2 or not tld.isalpha():
                    raise ValueError('Email must have a valid domain with at least 2 letters after the dot')
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = ProjectStatus.ACTIVE
    priority: Optional[int] = Field(1, ge=0)
    budget: Optional[float] = Field(None, ge=0)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[int] = None
    budget: Optional[float] = None


class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    is_public: bool
    tasks: Optional[List['TaskResponse']] = []

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.PENDING
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    assigned_to_id: int
    project_id: Optional[int] = None
    planned_hours: Optional[float] = Field(0.0, ge=0, le=1000)
    actual_hours: Optional[float] = Field(0.0, ge=0, le=1000)
    deadline: Optional[datetime] = None
    tags: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_to_id: Optional[int] = None
    project_id: Optional[int] = None
    planned_hours: Optional[float] = Field(None, ge=0, le=1000)
    actual_hours: Optional[float] = Field(None, ge=0, le=1000)
    deadline: Optional[datetime] = None
    tags: Optional[str] = None


class TaskResponse(TaskBase):
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class TokenResponse(BaseModel):
    session_id: str
    user_id: int
    username: str


class StatusDistribution(BaseModel):
    status: str
    count: int


class PriorityDistribution(BaseModel):
    priority: str
    count: int


class UserWorkload(BaseModel):
    user_id: int
    username: str
    planned_hours: float
    actual_hours: float
    task_count: int


class StatsOverview(BaseModel):
    total_tasks: int
    status_distribution: List[StatusDistribution]
    priority_distribution: List[PriorityDistribution]
    user_workload: List[UserWorkload]
    overdue_tasks: int
    completed_tasks: int
    completion_rate: float