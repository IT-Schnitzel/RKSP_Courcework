from passlib.context import CryptContext
from .redis_client import redis_client
import secrets
from .config import Config

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    if not plain_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    if not password:
        raise ValueError("Password cannot be empty")
    return pwd_context.hash(password)

def create_session(user_id: int) -> str:
    session_id = secrets.token_urlsafe(32)
    expire_seconds = Config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    redis_client.setex(f"session:{session_id}", expire_seconds, str(user_id))
    return session_id

def get_user_id_from_session(session_id: str) -> int:
    user_id = redis_client.get(f"session:{session_id}")
    if user_id is None:
        return None
    return int(user_id)

def delete_session(session_id: str):
    redis_client.delete(f"session:{session_id}")