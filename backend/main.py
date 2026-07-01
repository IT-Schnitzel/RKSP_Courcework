import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, tasks, projects, stats
from .database import engine, Base

PORT = os.getenv("PORT", "8000")
print(f"🚀 Starting server on port {PORT}")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(projects.router)
app.include_router(stats.router)

@app.get("/")
def root():
    return {"message": "Task Manager API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}