from core.db_session import get_db
from core.api.user.views import get_current_user
import math
from main import app
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from modules.filter.models import TBL_FILTER
from modules.filter.schemas import *

@app.post(
    "/create_filter",
    tags=["Filter"],
    status_code=201,
    operation_id="create_filter",
    dependencies=[Depends(get_current_user)],
)
async def create_filter(
    filter: FilterModel = Depends(FilterModel.form),
    db      : Session        = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Insert the new record
    new_item = TBL_FILTER(
        id            = new_id,
        name          = filter.name,
        active        = filter.active
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    data = filter_response(new_item)

    return {
        "ok"     : True,
        "status" : 201,
        "title"  : "Filter",
        "message": "Data created successfully",
        "data"   : data,
        "error"  : {},
    }


@app.get(
    "/get_filter",
    tags=["Filter"],
    operation_id="get_filter",
    dependencies=[Depends(get_current_user)],
)
async def get_filter(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_FILTER).filter(TBL_FILTER.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_FILTER.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [filter_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Filter',
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
    "/get_filter/{filter_id}",
    tags=["filter"],
    operation_id="get_filter_by_id",
    dependencies=[Depends(get_current_user)],
)
async def get_filter_by_id(
    filter_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_FILTER).filter(TBL_FILTER.id == filter_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "filter not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "filter",
        "message": "Data retrieved successfully",
        "data"   : filter_response(item),
        "error"  : {},
    }


@app.put(
    "/update_filter/{filter_id}",
    tags         = ["filter"],
    operation_id = "update_filter",
    dependencies = [Depends(get_current_user)],
)
async def update_filter(
    filter_id: str,
    filter   : FilterModel = Depends(FilterModel.form),
    db         : Session        = Depends(get_db),
):
    item = db.query(TBL_FILTER).filter(TBL_FILTER.id == filter_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "filter not found",
    )
    setattr(item, "name", filter.name)
    setattr(item, "active", filter.active)

    db.commit()
    db.refresh(item)
    
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "filter",
        "message": "Data updated successfully",
        "data"   : filter_response(item),
        "error"  : {},
    }


@app.delete(
    "/delete_filter/{filter_id}",
    tags         = ["filter"],
    operation_id = "delete_filter",
    dependencies = [Depends(get_current_user)],
)
async def delete_filter(
    filter_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_FILTER).filter(TBL_FILTER.id == filter_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Filter not found",
        )

    data = filter_response(item)
    db.delete(item)
    db.commit()

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "filter",
        "message": "Data deleted successfully",
        "data"   : data,
        "error"  : {},
    }
