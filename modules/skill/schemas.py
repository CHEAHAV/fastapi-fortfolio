from typing import Any, cast
from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.prefix_id import generate_prefixed_id
from core.upload_utils import media_name, media_url, upload_image_to_cloudinary
from modules.skill.models import TBL_SKILL


class SkillSchema(BaseModel):
    id         : str | None = None
    name       : str | None = None
    score      : float | None = None
    description: str | None = None
    image      : UploadFile | None = None
    active     : bool


class SkillModel(SkillSchema):
    @classmethod
    def form(
        cls,
        name        : str        = Form(None, examples=[""]),
        score       : float      = Form(None, examples=[""]),
        description : str        = Form(None, examples=[""]),
        image       : UploadFile = File(None),
        active      : bool       = True,
    ):
        return cls(
            name        = name,
            score       = score,
            description = description,
            image       = image,
            active      = active,
        )

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_SKILL
    ], "SKL")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result

def save_image(image: UploadFile) -> str:
    return upload_image_to_cloudinary(image, "Skill")


def skill_response(item: Any) -> dict[str, Any]:
    image = cast(str | None, getattr(item, "image"))
    return {
        "id"         : getattr(item, "id"),
        "name"       : getattr(item, "name"),
        "score"      : getattr(item, "score"),
        "description": getattr(item, "description"),
        "image"      : media_name(image),
        "image_link" : media_url(image),
        "active"     : getattr(item, "active"),
    }