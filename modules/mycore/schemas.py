from typing import Any, cast
from fastapi import File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel, HttpUrl, TypeAdapter, ValidationError, field_validator
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from core.prefix_id import generate_prefixed_id
from core.upload_utils import media_name, media_url, upload_image_to_cloudinary
from modules.mycore.models import TBL_MY_CORE


class MyCoreSchema(BaseModel):
    id          : str | None = None
    name        : str | None = None
    description : str | None = None
    official_url: str | None = None
    image       : UploadFile | None = None
    active      : bool

    @field_validator("official_url")
    @classmethod
    def validate_official_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return ""
        if len(value) > 2048:
            raise ValueError("Official website URL must be at most 2048 characters")
        url = TypeAdapter(HttpUrl).validate_python(value)
        if url.username or url.password:
            raise ValueError("Official website URL must not contain login credentials")
        return str(url)

class MyCoreModel(MyCoreSchema):
    @classmethod
    async def form(
        cls,
        request: Request,
        name        : str        = Form(None, examples=[""]),
        description : str        = Form(None, examples=[""]),
        image       : UploadFile = File(None),
        active      : bool       = True,
        official_url: str | None = Form(None, max_length=2048, description="Official technology website (https://...)"),
    ):
        # FastAPI maps an empty optional form field to None. Preserve the
        # difference between an omitted link and an explicit request to clear it.
        if official_url is None and "official_url" in await request.form():
            official_url = ""
        try:
            return cls(
                name        = name,
                description = description,
                image       = image,
                active      = active,
                official_url = official_url,
            )
        except ValidationError as error:
            raise RequestValidationError([
                {**item, "loc": ("body", *item["loc"])}
                for item in error.errors()
            ]) from error

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_MY_CORE
    ], "MYC")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result

def save_image(image: UploadFile) -> str:
    return upload_image_to_cloudinary(image, "MyCore")


def mycore_response(item: Any) -> dict[str, Any]:
    image = cast(str | None, getattr(item, "image"))
    return {
        "id"         : getattr(item, "id"),
        "name"       : getattr(item, "name"),
        "description": getattr(item, "description"),
        "official_url": getattr(item, "official_url", None),
        "image"      : media_name(image),
        "image_link" : media_url(image),
        "active"     : getattr(item, "active"),
    }
