from core.db_session import get_db
from core.api.user.views import get_current_user
from core.upload_utils import delete_cloudinary_image
import math
from typing import cast
from main import app
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from modules.info.models import TBL_INFO
from modules.info.schemas import *

@app.post(
    "/create_info",
    tags=["info"],
    status_code=201,
    operation_id="create_info",
    dependencies=[Depends(get_current_user)],
)
async def create_info(
    info: InfoModel = Depends(InfoModel.form),
    db      : Session        = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Persist the image (if provided)
    image_filename: str | None = None
    if info.image and info.image.filename:
        image_filename = save_image(info.image)

    # 3. Insert the new record
    new_item = TBL_INFO(
        id            = new_id,
        name          = info.name,
        description   = info.description,
        image         = image_filename,
        active        = info.active
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    data = info_response(new_item)

    return {
        "ok"     : True,
        "status" : 201,
        "title"  : "info",
        "message": "Data created successfully",
        "data"   : data,
        "error"  : {},
    }


@app.get(
    "/get_info",
    tags=["info"],
    operation_id="get_info",
    dependencies=[Depends(get_current_user)],
)
async def get_info(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_INFO).filter(TBL_INFO.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_INFO.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [info_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'info',
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
    "/get_info/{info_id}",
    tags=["info"],
    operation_id="get_info_by_id",
    dependencies=[Depends(get_current_user)],
)
async def get_info_by_id(
    info_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_INFO).filter(TBL_INFO.id == info_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "info not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "info",
        "message": "Data retrieved successfully",
        "data"   : info_response(item),
        "error"  : {},
    }


@app.put(
    "/update_info/{info_id}",
    tags         = ["info"],
    operation_id = "update_info",
    dependencies = [Depends(get_current_user)],
)
async def update_info(
    info_id: str,
    info   : InfoModel = Depends(InfoModel.form),
    db         : Session        = Depends(get_db),
):
    item = db.query(TBL_INFO).filter(TBL_INFO.id == info_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "info not found",
    )
    setattr(item, "name", info.name)
    setattr(item, "description", info.description)
    setattr(item, "active", info.active)
    if info.image and info.image.filename:
        old_image = cast(str | None, getattr(item, "image", None))
        setattr(item, "image", save_image(info.image))
        delete_cloudinary_image(old_image)

    db.commit()
    db.refresh(item)
    
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "info",
        "message": "Data updated successfully",
        "data"   : info_response(item),
        "error"  : {},
    }


@app.delete(
    "/delete_info/{info_id}",
    tags         = ["info"],
    operation_id = "delete_info",
    dependencies = [Depends(get_current_user)],
)
async def delete_info(
    info_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_INFO).filter(TBL_INFO.id == info_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "info not found",
        )

    data = info_response(item)
    image = cast(str | None, getattr(item, "image", None))
    delete_cloudinary_image(image)
    db.delete(item)
    db.commit()

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "info",
        "message": "Data deleted successfully",
        "data"   : data,
        "error"  : {},
    }
