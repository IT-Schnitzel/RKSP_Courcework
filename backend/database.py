import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError
from .config import Config

# Если DATABASE_URL не задан или это хост "host"/"db" (Docker/Railway default), используем SQLite
if not Config.DATABASE_URL or "host" in Config.DATABASE_URL or "db" in Config.DATABASE_URL:
    Config.DATABASE_URL = "sqlite:///./app.db"
    print("⚠️ Using SQLite (DATABASE_URL not properly configured)")

# Повторные попытки подключения к БД (для Railway)
max_retries = 5
retry_delay = 5

for attempt in range(max_retries):
    try:
        engine = create_engine(Config.DATABASE_URL, echo=Config.DEBUG)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print(f"✅ Database connected successfully (attempt {attempt + 1})")
        break
    except OperationalError as e:
        print(f"⚠️ Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
        else:
            print("❌ Failed to connect to database after all retries, using SQLite")
            Config.DATABASE_URL = "sqlite:///./app.db"
            engine = create_engine(Config.DATABASE_URL, echo=Config.DEBUG)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()