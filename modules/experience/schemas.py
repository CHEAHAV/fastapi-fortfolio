from typing import Any, cast
from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.prefix_id import generate_prefixed_id
from core.upload_utils import media_name, media_url, upload_image_to_cloudinary
from modules.experience.models import TBL_EXPERIENCE

class ExperienceSchema(BaseModel):
    id      : str | None = None
    year_exp: str | None = None
    project : str | None = None
    commit  : str | None = None
    active  : bool


class ExperienceModel(ExperienceSchema):
    @classmethod
    def form(
        cls,
        year_exp : str  = Form(None, examples=[""]),
        project  : str  = Form(None, examples=[""]),
        commit   : str  = Form(None, examples=[""]),
        active   : bool = Form(None),
    ):
        return cls(
            year_exp = year_exp,
            project  = project,
            commit   = commit,
            active   = active,
        )

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_EXPERIENCE
    ], "EXP")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result

def experience_response(item: Any) -> dict[str, Any]:
    return {
        "id"      : getattr(item, "id"),
        "year_exp": getattr(item, "year_exp"),
        "project" : getattr(item, "project"),
        "commit"  : getattr(item, "commit"),
        "active"  : getattr(item, "active"),
    }