from typing import Any, cast
from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.prefix_id import generate_prefixed_id
from core.upload_utils import media_name, media_url, upload_icon_to_cloudinary
from modules.social.models import TBL_SOCIAL


class ContactMeSchema(BaseModel):
    id         : str | None = None
    name       : str | None = None
    description: str | None = None
    icon       : UploadFile | None = None
    active     : bool


class ContactMeModel(ContactMeSchema):
    @classmethod
    def form(
        cls,
        name        : str        = Form(None, examples=[""]),
        description : str        = Form(None, examples=[""]),
        icon        : UploadFile = File(None),
        active      : bool       = True,
    ):
        return cls(
            name        = name,
            description = description,
            icon        = icon,
            active      = active,
        )

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_SOCIAL
    ], "CTM")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result

def save_icon(icon: UploadFile) -> str:
    return upload_icon_to_cloudinary(icon, "Contact Me")


def contact_me_response(item: Any) -> dict[str, Any]:
    icon = cast(str | None, getattr(item, "icon"))
    return {
        "id"         : getattr(item, "id"),
        "name"       : getattr(item, "name"),
        "description": getattr(item, "description"),
        "icon"       : media_name(icon),
        "icon_link"  : media_url(icon),
        "active"     : getattr(item, "active"),
    }