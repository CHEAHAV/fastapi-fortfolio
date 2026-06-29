from core.db_session import get_db
from core.api.user.views import get_current_user
from core.upload_utils import delete_cloudinary_image
import math
from typing import cast
from main import app
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from modules.mycore.models import TBL_MY_CORE
from modules.mycore.schemas import *

@app.post(
    "/create_mycore",
    tags=["Mycore"],
    status_code=201,
    operation_id="create_mycore",
    dependencies=[Depends(get_current_user)],
)
async def create_mycore(
    mycore: MyCoreModel = Depends(MyCoreModel.form),
    db      : Session        = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Persist the image (if provided)
    image_filename: str | None = None
    if mycore.image and mycore.image.filename:
        image_filename = save_image(mycore.image)

    # 3. Insert the new record
    new_item = TBL_MY_CORE(
        id            = new_id,
        name          = mycore.name,
        description   = mycore.description,
        image         = image_filename,
        active        = mycore.active
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    data = mycore_response(new_item)

    return {
        "ok"     : True,
        "status" : 201,
        "title"  : "Mycore",
        "message": "Data created successfully",
        "data"   : data,
        "error"  : {},
    }


@app.get(
    "/get_mycore",
    tags=["Mycore"],
    operation_id="get_mycore",
    dependencies=[Depends(get_current_user)],
)
async def get_mycore(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_MY_CORE).filter(TBL_MY_CORE.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_MY_CORE.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [mycore_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Mycore',
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
    "/get_mycore/{mycore_id}",
    tags=["Mycore"],
    operation_id="get_mycore_by_id",
    dependencies=[Depends(get_current_user)],
)
async def get_mycore_by_id(
    mycore_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_MY_CORE).filter(TBL_MY_CORE.id == mycore_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Mycore not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Mycore",
        "message": "Data retrieved successfully",
        "data"   : mycore_response(item),
        "error"  : {},
    }


@app.put(
    "/update_mycore/{mycore_id}",
    tags         = ["Mycore"],
    operation_id = "update_mycore",
    dependencies = [Depends(get_current_user)],
)
async def update_mycore(
    mycore_id: str,
    mycore   : MyCoreModel = Depends(MyCoreModel.form),
    db         : Session        = Depends(get_db),
):
    item = db.query(TBL_MY_CORE).filter(TBL_MY_CORE.id == mycore_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Mycore not found",
    )
    setattr(item, "name", mycore.name)
    setattr(item, "description", mycore.description)
    setattr(item, "active", mycore.active)
    if mycore.image and mycore.image.filename:
        old_image = cast(str | None, getattr(item, "image", None))
        setattr(item, "image", save_image(mycore.image))
        delete_cloudinary_image(old_image)

    db.commit()
    db.refresh(item)
    
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Mycore",
        "message": "Data updated successfully",
        "data"   : mycore_response(item),
        "error"  : {},
    }


@app.delete(
    "/delete_mycore/{mycore_id}",
    tags         = ["Mycore"],
    operation_id = "delete_mycore",
    dependencies = [Depends(get_current_user)],
)
async def delete_mycore(
    mycore_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_MY_CORE).filter(TBL_MY_CORE.id == mycore_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Mycore not found",
        )

    data = mycore_response(item)
    image = cast(str | None, getattr(item, "image", None))
    delete_cloudinary_image(image)
    db.delete(item)
    db.commit()

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Mycore",
        "message": "Data deleted successfully",
        "data"   : data,
        "error"  : {},
    }
