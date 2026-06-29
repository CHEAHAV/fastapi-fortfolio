import math
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from core.db_session import get_db
from main import website
from modules.filter.models import TBL_FILTER
from modules.filter.schemas import filter_response

@website.get(
    "/get_filter",
    tags=["Filter"],
    operation_id="get_filter",
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


@website.get(
    "/get_filter/{filter_id}",
    tags=["Filter"],
    operation_id="get_filter_by_id",
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
