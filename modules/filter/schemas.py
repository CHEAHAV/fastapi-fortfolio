from typing import Any
from fastapi import Form, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.prefix_id import generate_prefixed_id
from modules.filter.models import TBL_FILTER


class FilterSchema(BaseModel):
    id     : str  | None = None
    name   : str  | None = None
    active : bool | None = None


class FilterModel(FilterSchema):
    @classmethod
    def form(
        cls,
        name   : str  = Form(None, examples=[""]),
        active : bool = Form(None),
    ):
        return cls(
            name   = name,
            active = active,
        )

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_FILTER
    ], "FIL")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result

def filter_response(item: Any) -> dict[str, Any]:
    return {
        "id"             : getattr(item, "id"),
        "name"           : getattr(item, "name"),
        "active"         : getattr(item, "active"),
    }