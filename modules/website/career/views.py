import math
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from core.db_session import get_db
from main import website
from modules.career.models import TBL_CAREER
from modules.career.schemas import career_response

@website.get(
    "/get_career",
    tags=["career"],
    operation_id="get_career",
)
async def get_career(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_CAREER).filter(TBL_CAREER.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_CAREER.name\
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


@website.get(
    "/get_career/{career_id}",
    tags=["Career"],
    operation_id="get_career_by_id",
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
