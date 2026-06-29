from typing import Any
from fastapi import Form, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .models import TBL_MESSAGE
from core.prefix_id import generate_prefixed_id

class MessageSchema(BaseModel):
    id        : str | None = None
    first_name: str | None = None
    last_name : str | None = None
    email     : str | None = None
    subject   : str | None = None
    message   : str | None = None
    active    : bool = True


class MessageModel(MessageSchema):
    @classmethod
    def form(
        cls,
        first_name : str  = Form(None, examples=[""]),
        last_name  : str  = Form(None, examples=[""]),
        email      : str  = Form(None, examples=[""]),
        subject    : str  = Form(None, examples=[""]),
        message    : str  = Form(None, examples=[""]),
        active     : bool = Form(True),
    ):
        return cls(
            first_name = first_name,
            last_name  = last_name,
            email      = email,
            subject    = subject,
            message    = message,
            active     = active,
        )

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_MESSAGE
    ], "FIL")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result

def message_response(item: Any) -> dict[str, Any]:
    return {
        "id"        : getattr(item, "id"),
        "first_name": getattr(item, "first_name"),
        "last_name" : getattr(item, "last_name"),
        "email"     : getattr(item, "email"),
        "subject"   : getattr(item, "subject"),
        "message"   : getattr(item, "message"),
        "active"    : getattr(item, "active"),
    }
