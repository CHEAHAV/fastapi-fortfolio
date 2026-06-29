from core.db_session import get_db
from core.api.user.views import get_current_user
from core.upload_utils import delete_cloudinary_icon
import math
from typing import cast
from main import app
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from modules.contact_me.models import TBL_CONTACT_ME
from modules.contact_me.schemas import *

@app.post(
    "/create_contact_me",
    tags=["Contact Me"],
    status_code=201,
    operation_id="create_contact_me",
    dependencies=[Depends(get_current_user)],
)
async def create_contact_me(
    contact_me: ContactMeModel = Depends(ContactMeModel.form),
    db      : Session        = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Persist the icon (if provided)
    icon_filename: str | None = None
    if contact_me.icon and contact_me.icon.filename:
        icon_filename = save_icon(contact_me.icon)

    # 3. Insert the new record
    new_item = TBL_CONTACT_ME(
        id          = new_id,
        name        = contact_me.name,
        description = contact_me.description,
        icon        = icon_filename,
        contact_url = normalize_contact_url(contact_me.description, contact_me.contact_url),
        active      = contact_me.active
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    data = contact_me_response(new_item)

    return {
        "ok"     : True,
        "status" : 201,
        "title"  : "contact_me",
        "message": "Data created successfully",
        "data"   : data,
        "error"  : {},
    }


@app.get(
    "/get_contact_me",
    tags=["Contact Me"],
    operation_id="get_contact_me",
    dependencies=[Depends(get_current_user)],
)
async def get_contact_me(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_CONTACT_ME).filter(TBL_CONTACT_ME.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_CONTACT_ME.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [contact_me_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'contact_me',
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
    "/get_contact_me/{contact_me_id}",
    tags=["Contact Me"],
    operation_id="get_contact_me_by_id",
    dependencies=[Depends(get_current_user)],
)
async def get_contact_me_by_id(
    contact_me_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_CONTACT_ME).filter(TBL_CONTACT_ME.id == contact_me_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "contact_me not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "contact_me",
        "message": "Data retrieved successfully",
        "data"   : contact_me_response(item),
        "error"  : {},
    }


@app.put(
    "/update_contact_me/{contact_me_id}",
    tags         = ["Contact Me"],
    operation_id = "update_contact_me",
    dependencies = [Depends(get_current_user)],
)
async def update_contact_me(
    contact_me_id: str,
    contact_me   : ContactMeModel = Depends(ContactMeModel.form),
    db         : Session        = Depends(get_db),
):
    item = db.query(TBL_CONTACT_ME).filter(TBL_CONTACT_ME.id == contact_me_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "contact_me not found",
    )
    setattr(item, "name", contact_me.name)
    setattr(item, "description", contact_me.description)
    setattr(item, "contact_url", normalize_contact_url(contact_me.description, contact_me.contact_url))
    setattr(item, "active", contact_me.active)
    if contact_me.icon and contact_me.icon.filename:
        old_icon = cast(str | None, getattr(item, "icon", None))
        setattr(item, "icon", save_icon(contact_me.icon))
        delete_cloudinary_icon(old_icon)

    db.commit()
    db.refresh(item)
    
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "contact_me",
        "message": "Data updated successfully",
        "data"   : contact_me_response(item),
        "error"  : {},
    }


@app.delete(
    "/delete_contact_me/{contact_me_id}",
    tags         = ["Contact Me"],
    operation_id = "delete_contact_me",
    dependencies = [Depends(get_current_user)],
)
async def delete_contact_me(
    contact_me_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_CONTACT_ME).filter(TBL_CONTACT_ME.id == contact_me_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "contact_me not found",
        )

    data = contact_me_response(item)
    icon = cast(str | None, getattr(item, "icon", None))
    delete_cloudinary_icon(icon)
    db.delete(item)
    db.commit()

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "contact_me",
        "message": "Data deleted successfully",
        "data"   : data,
        "error"  : {},
    }
