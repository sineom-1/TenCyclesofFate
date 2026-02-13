from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status, Cookie
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings
from . import auth_store

# --- Setup ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Models ---
class TokenData(object):
    username: str | None = None
    trust_level: int | None = 0

# --- Core Functions ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def normalize_username(username: str) -> str:
    return username.strip()


def validate_username(username: str) -> str | None:
    normalized = normalize_username(username)
    if not normalized:
        return "用户名不能为空"
    if len(normalized) < 3:
        return "用户名至少 3 个字符"
    if len(normalized) > 32:
        return "用户名不能超过 32 个字符"
    if not all(char.isalnum() or char in {"_", "-"} for char in normalized):
        return "用户名只能包含字母、数字、下划线和中划线"
    return None


def validate_password(password: str) -> str | None:
    if len(password) < 8:
        return "密码至少 8 位"
    return None


def create_login_payload(user: dict) -> dict:
    return {
        "sub": user["username"],
        "id": user["id"],
        "name": user["username"],
        "trust_level": 0,
    }


def authenticate_user(username: str, password: str) -> dict | None:
    normalized = normalize_username(username)
    user = auth_store.get_user_by_username(normalized)
    if user is None:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return {
        "id": user["id"],
        "username": user["username"],
    }

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """Decodes the access token and returns the payload."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception

# --- FastAPI Dependencies ---
async def get_current_user(token: Annotated[str | None, Cookie()] = None):
    """
    Decodes JWT from cookie and returns user info.
    Raises HTTP 401 if token is missing, invalid, or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # The JWT payload contains user identity from local auth
        user = {
            "username": username,
            "trust_level": payload.get("trust_level", 0),
            "id": payload.get("id"),
            "name": payload.get("name"),
        }
    except JWTError:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[dict, Depends(get_current_user)]
):
    # In a real app, you might check if the user is active
    return current_user
