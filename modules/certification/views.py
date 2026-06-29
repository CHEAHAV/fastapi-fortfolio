from core.db_session import get_db
from core.api.user.views import get_current_user
from core.upload_utils import delete_cloudinary_icon
import math
from typing import cast
from main import app
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from modules.certification.models import TBL_CERTIFICATION
from modules.certification.schemas import *

@app.post(
    "/create_certification",
    tags=["Certification"],
    status_code=201,
    operation_id="create_certification",
    dependencies=[Depends(get_current_user)],
)
async def create_certification(
    certification: CertificationModel = Depends(CertificationModel.form),
    db      : Session        = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Persist the icon (if provided)
    icon_filename: str | None = None
    if certification.icon and certification.icon.filename:
        icon_filename = save_icon(certification.icon)

    # 3. Insert the new record
    new_item = TBL_CERTIFICATION(
        id              = new_id,
        name            = certification.name,
        issuer          = certification.issuer,
        date_earned     = certification.date_earned,
        credential_id   = certification.credential_id,
        certificate_url = certification.certificate_url,
        icon            = icon_filename,
        active          = certification.active
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    data = certification_response(new_item)

    return {
        "ok"     : True,
        "status" : 201,
        "title"  : "Certification",
        "message": "Data created successfully",
        "data"   : data,
        "error"  : {},
    }


@app.get(
    "/get_certification",
    tags=["Certification"],
    operation_id="get_certification",
    dependencies=[Depends(get_current_user)],
)
async def get_certification(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_CERTIFICATION).filter(TBL_CERTIFICATION.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_CERTIFICATION.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [certification_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Certification',
        'message': 'Data retrieved successfully',
        'data'   : {
            'lists'    : data_list,
            'meta_data': {
                'total'       : total,
                'total_page'  : total_pages,
                'current_page': page,
                'size'        : size,
            }
        },
        'error': {}
    }


@app.get(
    "/get_certification/{certificate_id}",
    tags=["Certification"],
    operation_id="get_certification_by_id",
    dependencies=[Depends(get_current_user)],
)
async def get_certification_by_id(
    certificate_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_CERTIFICATION).filter(TBL_CERTIFICATION.id == certificate_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Certification not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Certification",
        "message": "Data retrieved successfully",
        "data"   : certification_response(item),
        "error"  : {},
    }


@app.put(
    "/update_certificate/{certificate_id}",
    tags         = ["Certification"],
    operation_id = "update_certificate",
    dependencies = [Depends(get_current_user)],
)
async def update_certificate(
    certificate_id: str,
    certificate   : CertificationModel = Depends(CertificationModel.form),
    db         : Session        = Depends(get_db),
):
    item = db.query(TBL_CERTIFICATION).filter(TBL_CERTIFICATION.id == certificate_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Certificate not found",
    )
    setattr(item, "name", certificate.name)
    setattr(item, "title", certificate.title)
    setattr(item, "issuer", certificate.issuer)
    setattr(item, "date_earned", certificate.date_earned)
    setattr(item, "credential_id", certificate.credential_id)
    setattr(item, "certificate_url", certificate.certificate_url)
    setattr(item, "active", certificate.active)
    if certificate.icon and certificate.icon.filename:
        old_icon = cast(str | None, getattr(item, "icon", None))
        setattr(item, "icon", save_icon(certificate.icon))
        delete_cloudinary_icon(old_icon)

    db.commit()
    db.refresh(item)
    
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Certification",
        "message": "Data updated successfully",
        "data"   : certification_response(item),
        "error"  : {},
    }


@app.delete(
    "/delete_certificate/{certificate_id}",
    tags         = ["Certification"],
    operation_id = "delete_certificate",
    dependencies = [Depends(get_current_user)],
)
async def delete_certificate(
    certificate_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_CERTIFICATION).filter(TBL_CERTIFICATION.id == certificate_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Certification not found",
        )

    data = certification_response(item)
    icon = cast(str | None, getattr(item, "icon", None))
    delete_cloudinary_icon(icon)
    db.delete(item)
    db.commit()

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Certification",
        "message": "Data deleted successfully",
        "data"   : data,
        "error"  : {},
    }
