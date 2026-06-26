from typing import Any, cast
from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.prefix_id import generate_prefixed_id
from core.upload_utils import media_name, media_url, upload_image_to_cloudinary
from modules.project.models import TBL_PROJECT

class ProjectSchema(BaseModel):
    id         : str | None = None
    name       : str | None = None
    description: str | None = None
    duration   : str | None = None
    role       : str | None = None
    platform   : str | None = None
    challenge  : str | None = None
    project_url: str | None = None
    image      : UploadFile | None = None
    active     : bool


class ProjectModel(ProjectSchema):
    @classmethod
    def form(
        cls,
        name        : str        = Form(None, examples=[""]),
        description : str        = Form(None, examples=[""]),
        duration    : str        = Form(None, examples=[""]),
        role        : str        = Form(None, examples=[""]),
        platform    : str        = Form(None, examples=[""]),
        challenge   : str        = Form(None, examples=[""]),
        project_url : str        = Form(None, examples=[""]),
        image       : UploadFile = File(None),
        active      : bool       = True,
    ):
        return cls(
            name        = name,
            description = description,
            duration    = duration,
            role        = role,
            platform    = platform,
            challenge   = challenge,
            project_url = project_url,
            image       = image,
            active      = active,
        )

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_PROJECT
    ], "CAT")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result

def save_image(image: UploadFile) -> str:
    return upload_image_to_cloudinary(image, "Project")


def project_response(item: Any) -> dict[str, Any]:
    image = cast(str | None, getattr(item, "image"))
    return {
        "id"         : getattr(item, "id"),
        "name"       : getattr(item, "name"),
        "description": getattr(item, "description"),
        "duration"   : getattr(item, "duration"),
        "role"       : getattr(item, "role"),
        "platform"   : getattr(item, "platform"),
        "challenge"  : getattr(item, "challenge"),
        "project_url": getattr(item, "project_url"),
        "image"      : media_name(image),
        "image_link" : media_url(image),
        "active"     : getattr(item, "active"),
    }