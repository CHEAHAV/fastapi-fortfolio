import math
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from core.db_session import get_db
from main import website
from modules.info.models import TBL_INFO
from modules.info.schemas import info_response

@website.get(
    "/get_info",
    tags=["info"],
    operation_id="get_info",
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


@website.get(
    "/get_info/{info_id}",
    tags=["info"],
    operation_id="get_info_by_id",
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
