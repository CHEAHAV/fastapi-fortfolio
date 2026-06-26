from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import cast

from config import settings
from core.api.user.models import TBL_USER
from core.db_session import get_db


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def user_payload(user: TBL_USER) -> dict:
    return {
        "id"        : getattr(user, "id", ""),
        "username"  : getattr(user, "username", ""),
        "email"     : getattr(user, "email", None),
        "first_name": getattr(user, "first_name", None),
        "last_name" : getattr(user, "last_name", None),
        "phone"     : getattr(user, "phone", None),
        "photo"     : getattr(user, "photo", None),
        "role_id"   : getattr(user, "role_id", None),
        "is_active" : getattr(user, "is_active", True),
    }


def authenticate_user(db: Session, username: str, password: str) -> TBL_USER | None:
    user = (
        db.query(TBL_USER)
        .filter(or_(TBL_USER.username == username, TBL_USER.email == username, TBL_USER.id == username))
        .first()
    )
    if not user:
        return None

    is_active = cast(bool, getattr(user, "is_active", False))
    hashed_password = cast(str, getattr(user, "password", ""))
    if not is_active or not verify_password(password, hashed_password):
        return None
    return user


async def get_current_user(
    token: str     = Depends(oauth2_scheme),
    db   : Session = Depends(get_db),
) -> TBL_USER:
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail      = "Could not validate credentials",
        headers     = {"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    user = db.query(TBL_USER).filter(TBL_USER.id == user_id).first()
    if not user:
        raise credentials_exception
    return user


from main import app


@app.post("/auth/login", tags=["Auth"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db        : Session                  = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail  = "Incorrect username or password",
            headers = {"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={
            "sub": cast(str, getattr(user, "id", "")),
            "username": cast(str, getattr(user, "username", "")),
        }
    )
    return {
        "access_token": access_token,
        "token_type"  : "bearer",
        "user"        : user_payload(user),
    }


@app.get("/auth/me", tags=["Auth"])
async def read_current_user(current_user: TBL_USER = Depends(get_current_user)):
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Auth",
        "message": "Current user",
        "data"   : user_payload(current_user),
        "error"  : {},
    }
