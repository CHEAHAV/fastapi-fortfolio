from typing import Any, cast
from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.prefix_id import generate_prefixed_id
from core.upload_utils import media_name, media_url, upload_image_to_cloudinary
from modules.study.models import TBL_STUDY

class StudySchema(BaseModel):
    id         : str | None = None
    title      : str | None = None
    sub_title  : str | None = None
    description: str | None = None
    date       : str | None = None
    active     : bool


class StudyModel(StudySchema):
    @classmethod
    def form(
        cls,
        title       : str  = Form(None, examples=[""]),
        sub_title   : str  = Form(None, examples=[""]),
        description : str  = Form(None, examples=[""]),
        date        : str  = Form(None, examples=[""]),
        active      : bool = Form(None),
    ):
        return cls(
            title       = title,
            sub_title   = sub_title,
            description = description,
            date        = date,
            active      = active,
        )

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_STUDY
    ], "STU")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result

def study_response(item: Any) -> dict[str, Any]:
    return {
        "id"         : getattr(item, "id"),
        "title"      : getattr(item, "title"),
        "sub_title"  : getattr(item, "sub_title"),
        "description": getattr(item, "description"),
        "date"       : getattr(item, "date"),
        "active"     : getattr(item, "active"),
    }