import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    REDIS_URL = os.getenv("REDIS_URL")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    print(f"🔍 DATABASE_URL: {'✅ set' if DATABASE_URL else '❌ NOT SET'}")
    print(f"🔍 REDIS_URL: {'✅ set' if REDIS_URL else '❌ NOT SET'}")
    print(f"🔍 SECRET_KEY: {'✅ set' if SECRET_KEY else '❌ NOT SET'}")