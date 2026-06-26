from typing import Any, cast
from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.prefix_id import generate_prefixed_id
from core.upload_utils import media_name, media_url, upload_icon_to_cloudinary
from modules.story.models import TBL_STORY


class StorySchema(BaseModel):
    id         : str | None = None
    title      : str | None = None
    description: str | None = None
    icon_name  : str | None = None
    icon       : UploadFile | None = None
    active     : bool


class StoryModel(StorySchema):
    @classmethod
    def form(
        cls,
        title       : str        = Form(None, examples=[""]),
        description : str        = Form(None, examples=[""]),
        icon_name   : str        = Form(None, examples=[""]),
        icon        : UploadFile = File(None),
        active      : bool       = True,
    ):
        return cls(
            title       = title,
            description = description,
            icon_name   = icon_name,
            icon        = icon,
            active      = active,
        )

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_STORY
    ], "STO")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result

def save_icon(icon: UploadFile) -> str:
    return upload_icon_to_cloudinary(icon, "Story")


def story_response(item: Any) -> dict[str, Any]:
    icon = cast(str | None, getattr(item, "icon"))
    return {
        "id"         : getattr(item, "id"),
        "title"      : getattr(item, "title"),
        "description": getattr(item, "description"),
        "icon_name"  : getattr(item, "icon_name"),
        "icon"       : media_name(icon),
        "icon_link"  : media_url(icon),
        "active"     : getattr(item, "active"),
    }