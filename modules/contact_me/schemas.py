import re
from typing import Any, cast
from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.prefix_id import generate_prefixed_id
from core.upload_utils import media_name, media_url, upload_icon_to_cloudinary
from modules.contact_me.models import TBL_CONTACT_ME


EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


class ContactMeSchema(BaseModel):
    id         : str | None = None
    name       : str | None = None
    description: str | None = None
    icon       : UploadFile | None = None
    contact_url: str | None = None
    active     : bool


class ContactMeModel(ContactMeSchema):
    @classmethod
    def form(
        cls,
        name        : str        = Form(None, examples=[""]),
        description : str        = Form(None, examples=[""]),
        icon        : UploadFile = File(None),
        contact_url : str        = Form(None, examples=[""]),
        active      : bool       = True,
    ):
        return cls(
            name        = name,
            description = description,
            icon        = icon,
            contact_url = contact_url,
            active      = active,
        )

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_CONTACT_ME
    ], "CTM")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result

def save_icon(icon: UploadFile) -> str:
    return upload_icon_to_cloudinary(icon, "Contact Me")


def normalize_contact_url(description: str | None, contact_url: str | None) -> str | None:
    url = (contact_url or "").strip()
    description_text = (description or "").strip()
    email_match = EMAIL_PATTERN.search(description_text)
    email = email_match.group(0) if email_match else None

    if email and not url:
        return f"mailto:{email}"

    if email and "mail.google.com" in url and "to=" not in url:
        return f"https://mail.google.com/mail/?view=cm&fs=1&to={email}"

    if email and url.lower() == email.lower():
        return f"mailto:{email}"

    return url or None


def contact_me_response(item: Any) -> dict[str, Any]:
    icon = cast(str | None, getattr(item, "icon"))
    return {
        "id"         : getattr(item, "id"),
        "name"       : getattr(item, "name"),
        "description": getattr(item, "description"),
        "icon"       : media_name(icon),
        "icon_link"  : media_url(icon),
        "contact_url": getattr(item, "contact_url"),
        "active"     : getattr(item, "active"),
    }
