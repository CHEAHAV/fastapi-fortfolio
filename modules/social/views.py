from core.db_session import get_db
from core.api.user.views import get_current_user
from core.upload_utils import delete_cloudinary_icon
import math
from typing import cast
from main import app
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from modules.social.models import TBL_SOCIAL
from modules.social.schemas import *

@app.post(
    "/create_social",
    tags=["Social"],
    status_code=201,
    operation_id="create_social",
    dependencies=[Depends(get_current_user)],
)
async def create_social(
    social: SocialModel = Depends(SocialModel.form),
    db      : Session        = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Persist the icon (if provided)
    icon_filename: str | None = None
    if social.icon and social.icon.filename:
        icon_filename = save_icon(social.icon)

    # 3. Insert the new record
    new_item = TBL_SOCIAL(
        id            = new_id,
        name          = social.name,
        icon         = icon_filename,
        active        = social.active
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    data = social_response(new_item)

    return {
        "ok"     : True,
        "status" : 201,
        "title"  : "Social",
        "message": "Data created successfully",
        "data"   : data,
        "error"  : {},
    }


@app.get(
    "/get_social",
    tags=["Social"],
    operation_id="get_social",
    dependencies=[Depends(get_current_user)],
)
async def get_social(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_SOCIAL).filter(TBL_SOCIAL.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_SOCIAL.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [social_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Social',
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
    "/get_social/{social_id}",
    tags=["Social"],
    operation_id="get_social_by_id",
    dependencies=[Depends(get_current_user)],
)
async def get_social_by_id(
    social_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_SOCIAL).filter(TBL_SOCIAL.id == social_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Social not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Social",
        "message": "Data retrieved successfully",
        "data"   : social_response(item),
        "error"  : {},
    }


@app.put(
    "/update_social/{social_id}",
    tags         = ["Social"],
    operation_id = "update_social",
    dependencies = [Depends(get_current_user)],
)
async def update_social(
    social_id: str,
    social   : SocialModel = Depends(SocialModel.form),
    db         : Session        = Depends(get_db),
):
    item = db.query(TBL_SOCIAL).filter(TBL_SOCIAL.id == social_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Social not found",
    )
    setattr(item, "name", social.name)
    setattr(item, "active", social.active)
    if social.icon and social.icon.filename: 
        setattr(item, "icon", save_icon(social.icon))

    db.commit()
    db.refresh(item)
    
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Social",
        "message": "Data updated successfully",
        "data"   : social_response(item),
        "error"  : {},
    }


@app.delete(
    "/delete_social/{social_id}",
    tags         = ["Social"],
    operation_id = "delete_social",
    dependencies = [Depends(get_current_user)],
)
async def delete_social(
    social_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_SOCIAL).filter(TBL_SOCIAL.id == social_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Social not found",
        )

    data = social_response(item)
    icon = cast(str | None, getattr(item, "icon", None))
    delete_cloudinary_icon(icon)
    db.delete(item)
    db.commit()

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Social",
        "message": "Data deleted successfully",
        "data"   : data,
        "error"  : {},
    }
