from core.db_session import get_db
from core.api.user.views import get_current_user
from core.upload_utils import delete_cloudinary_image
import math
from typing import cast
from main import app
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from modules.teach_stack.models import TBL_TEACH_STACK
from modules.teach_stack.schemas import *

@app.post(
    "/create_teach_stack",
    tags=["Teach Stack"],
    status_code=201,
    operation_id="create_teach_stack",
    dependencies=[Depends(get_current_user)],
)
async def create_teach_stack(
    teach_stack: TeachStackModel = Depends(TeachStackModel.form),
    db      : Session        = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Persist the image_left (if provided)
    image_left_filename: str | None = None
    if teach_stack.image_left and teach_stack.image_left.filename:
        image_left_filename = save_image(teach_stack.image_left)

    image_right_filename: str | None = None
    if teach_stack.image_right and teach_stack.image_right.filename:
        image_right_filename = save_image(teach_stack.image_right)

    # 3. Insert the new record
    new_item = TBL_TEACH_STACK(
        id          = new_id,
        name_left   = teach_stack.name_left,
        image_left  = image_left_filename,
        name_right  = teach_stack.name_right,
        image_right = image_right_filename,
        active      = teach_stack.active
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    data = teach_stack_response(new_item)

    return {
        "ok"     : True,
        "status" : 201,
        "title"  : "Teach Stack",
        "message": "Data created successfully",
        "data"   : data,
        "error"  : {},
    }


@app.get(
    "/get_teach_stack",
    tags=["Teach Stack"],
    operation_id="get_teach_stack",
    dependencies=[Depends(get_current_user)],
)
async def get_teach_stack(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_TEACH_STACK).filter(TBL_TEACH_STACK.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_TEACH_STACK.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [teach_stack_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Teack Stack',
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
    "/get_teach_stack/{teach_stack_id}",
    tags=["Teach Stack"],
    operation_id="get_teach_stack_by_id",
    dependencies=[Depends(get_current_user)],
)
async def get_teach_stack_by_id(
    teach_stack_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_TEACH_STACK).filter(TBL_TEACH_STACK.id == teach_stack_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "teach_stack not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Teach Stack",
        "message": "Data retrieved successfully",
        "data"   : teach_stack_response(item),
        "error"  : {},
    }


@app.put(
    "/update_teach_stack/{teach_stack_id}",
    tags         = ["Teach Stack"],
    operation_id = "update_teach_stack",
    dependencies = [Depends(get_current_user)],
)
async def update_teach_stack(
    teach_stack_id: str,
    teach_stack   : TeachStackModel = Depends(TeachStackModel.form),
    db         : Session        = Depends(get_db),
):
    item = db.query(TBL_TEACH_STACK).filter(TBL_TEACH_STACK.id == teach_stack_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Teach Stack not found",
    )
    setattr(item, "name_left", teach_stack.name_left)
    setattr(item, "name_right", teach_stack.name_right)
    setattr(item, "active", teach_stack.active)
    if teach_stack.image_left and teach_stack.image_left.filename: 
        setattr(item, "image_left", save_image(teach_stack.image_left))
    if teach_stack.image_right and teach_stack.image_right.filename: 
        setattr(item, "image_right", save_image(teach_stack.image_right))

    db.commit()
    db.refresh(item)
    
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Teach Stack",
        "message": "Data updated successfully",
        "data"   : teach_stack_response(item),
        "error"  : {},
    }


@app.delete(
    "/delete_teach_stack/{teach_stack_id}",
    tags         = ["Teach Stack"],
    operation_id = "delete_teach_stack",
    dependencies = [Depends(get_current_user)],
)
async def delete_teach_stack(
    teach_stack_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_TEACH_STACK).filter(TBL_TEACH_STACK.id == teach_stack_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Teach Stack not found",
        )

    data = teach_stack_response(item)
    image_left = cast(str | None, getattr(item, "image_left", None))
    delete_cloudinary_image(image_left)
    image_right = cast(str | None, getattr(item, "image_right", None))
    delete_cloudinary_image(image_right)
    db.delete(item)
    db.commit()

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Teach Stack",
        "message": "Data deleted successfully",
        "data"   : data,
        "error"  : {},
    }
