from core.db_session import get_db
from core.api.user.views import get_current_user
import math
from main import app
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from modules.career.models import TBL_CAREER
from modules.career.schemas import *

@app.post(
    "/create_career",
    tags=["Career"],
    status_code=201,
    operation_id="create_career",
    dependencies=[Depends(get_current_user)],
)
async def create_career(
    career: CareerModel = Depends(CareerModel.form),
    db      : Session        = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Insert the new record
    new_item = TBL_CAREER(
        id          = new_id,
        title       = career.title,
        sub_title   = career.sub_title,
        description = career.description,
        date        = career.date,
        active      = career.active
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    data = career_response(new_item)

    return {
        "ok"     : True,
        "status" : 201,
        "title"  : "career",
        "career": "Data created successfully",
        "data"   : data,
        "error"  : {},
    }


@app.get(
    "/get_career",
    tags=["Career"],
    operation_id="get_career",
    dependencies=[Depends(get_current_user)],
)
async def get_career(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_CAREER).filter(TBL_CAREER.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_CAREER.title\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [career_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'career',
        'career': 'Data retrieved successfully',
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
    "/get_career/{career_id}",
    tags=["Career"],
    operation_id="get_career_by_id",
    dependencies=[Depends(get_current_user)],
)
async def get_career_by_id(
    career_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_CAREER).filter(TBL_CAREER.id == career_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "career not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "career",
        "career": "Data retrieved successfully",
        "data"   : career_response(item),
        "error"  : {},
    }


@app.put(
    "/update_career/{career_id}",
    tags         = ["Career"],
    operation_id = "update_career",
    dependencies = [Depends(get_current_user)],
)
async def update_career(
    career_id: str,
    career   : CareerModel = Depends(CareerModel.form),
    db         : Session        = Depends(get_db),
):
    item = db.query(TBL_CAREER).filter(TBL_CAREER.id == career_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "career not found",
    )
    setattr(item, "title", career.title)
    setattr(item, "sub_title", career.sub_title)
    setattr(item, "description", career.description)
    setattr(item, "date", career.date)
    setattr(item, "active", career.active)

    db.commit()
    db.refresh(item)
    
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "career",
        "career": "Data updated successfully",
        "data"   : career_response(item),
        "error"  : {},
    }


@app.delete(
    "/delete_career/{career_id}",
    tags         = ["Career"],
    operation_id = "delete_career",
    dependencies = [Depends(get_current_user)],
)
async def delete_career(
    career_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_CAREER).filter(TBL_CAREER.id == career_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "career not found",
        )

    data = career_response(item)
    db.delete(item)
    db.commit()

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "career",
        "career": "Data deleted successfully",
        "data"   : data,
        "error"  : {},
    }
