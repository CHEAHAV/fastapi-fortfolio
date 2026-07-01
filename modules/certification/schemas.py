from datetime import date
from typing import Any, cast
from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.prefix_id import generate_prefixed_id
from core.upload_utils import media_name, media_url, upload_icon_to_cloudinary
from modules.certification.models import TBL_CERTIFICATION

class CertificationSchema(BaseModel):
    id              : str | None        = None
    name            : str | None        = None
    title           : str | None        = None
    issuer          : str | None        = None
    date_earned     : date | None       = None
    credential_id   : str | None        = None
    certificate_url: str | None         = None
    icon            : UploadFile | None = None
    active          : bool              = True

class CertificationModel(CertificationSchema):
    @classmethod
    def form(
        cls,
        name            : str        = Form(None, examples=[""]),
        title           : str        = Form(None, examples=[""]),
        issuer          : str        = Form(None, examples=[""]),
        date_earned     : date       = Form(None, examples=[""]),
        credential_id   : str        = Form(None, examples=[""]),
        certificate_url : str        = Form(None, examples=[""]),
        icon            : UploadFile = File(None),
        active          : bool       = True,
    ):
        return cls(
            name            = name,
            title           = title,
            issuer          = issuer,
            date_earned     = date_earned,
            credential_id   = credential_id,
            certificate_url = certificate_url,
            icon            = icon,
            active          = active,
        )

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_CERTIFICATION
    ], "CTC")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result

def save_icon(icon: UploadFile) -> str:
    return upload_icon_to_cloudinary(icon, "Certification")


def certification_response(item: Any) -> dict[str, Any]:
    icon = cast(str | None, getattr(item, "icon"))
    return {
        "id"             : getattr(item, "id"),
        "name"           : getattr(item, "name"),
        "title"          : getattr(item, "title"),
        "issuer"         : getattr(item, "issuer"),
        "date_earned"    : getattr(item, "date_earned"),
        "credential_id"  : getattr(item, "credential_id"),
        "certificate_url": getattr(item, "certificate_url"),
        "icon"           : media_name(icon),
        "icon_link"      : media_url(icon),
        "active"         : getattr(item, "active"),
    }
