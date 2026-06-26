from typing import Any, cast
from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.prefix_id import generate_prefixed_id
from core.upload_utils import media_name, media_url, upload_image_to_cloudinary
from modules.teach_stack.models import TBL_TEACH_STACK

class TeachStackSchema(BaseModel):
    id         : str | None = None
    name_left  : str | None = None
    image_left : UploadFile | None = None
    name_right : str | None = None
    image_right: UploadFile | None = None
    active     : bool


class TeachStackModel(TeachStackSchema):
    @classmethod
    def form(
        cls,
        name_left   : str        = Form(None, examples=[""]),
        image_left  : UploadFile = Form(None, examples=[""]),
        name_right  : str        = Form(None, examples=[""]),
        image_right : UploadFile = File(None),
        active      : bool       = True,
    ):
        return cls(
            name_left   = name_left,
            image_left  = image_left,
            name_right  = name_right,
            image_right = image_right,
            active      = active,
        )

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_TEACH_STACK
    ], "TST")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result

def save_image(image: UploadFile) -> str:
    return upload_image_to_cloudinary(image, "Teach Stack")


def teach_stack_response(item: Any) -> dict[str, Any]:
    image = cast(str | None, getattr(item, "image"))
    return {
        "id"              : getattr(item, "id"),
        "name_left"       : getattr(item, "name_left"),
        "image_left"      : media_name(image),
        "image_left_link" : media_url(image),
        "name_right"      : getattr(item, "name_right"),
        "image_right"     : media_name(image),
        "image_right_link": media_url(image),
        "active"          : getattr(item, "active"),
    }