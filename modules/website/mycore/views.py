import math
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from core.db_session import get_db
from main import website
from modules.mycore.models import TBL_MY_CORE
from modules.mycore.schemas import mycore_response


@website.get(
    "/get_mycore",
    tags=["Mycore"],
    operation_id="get_mycore", 
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


@website.get(
    "/get_mycore/{mycore_id}",
    tags=["Mycore"],
    operation_id="get_mycore_by_id",
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
