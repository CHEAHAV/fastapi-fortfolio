import math
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from modules.experience.schemas import experience_response
from modules.experience.models import TBL_EXPERIENCE
from core.db_session import get_db
from main import website

@website.get(
    "/get_experience",
    tags=["Experience"],
    operation_id="get_experience",
)
async def get_experience(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_EXPERIENCE).filter(TBL_EXPERIENCE.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_EXPERIENCE.id\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [experience_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'experience',
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
    "/get_experience/{experience_id}",
    tags=["Experience"],
    operation_id="get_experience_by_id",
)
async def get_experience_by_id(
    experience_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_EXPERIENCE).filter(TBL_EXPERIENCE.id == experience_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "experience not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "experience",
        "message": "Data retrieved successfully",
        "data"   : experience_response(item),
        "error"  : {},
    }
