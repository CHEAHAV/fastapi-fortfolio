import math
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from core.db_session import get_db
from main import website
from modules.study.models import TBL_STUDY
from modules.study.schemas import study_response

@website.get(
    "/get_study",
    tags=["Study"],
    operation_id="get_study",
)
async def get_study(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_STUDY).filter(TBL_STUDY.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_STUDY.title\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [study_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Study',
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
    "/get_study/{study_id}",
    tags=["Study"],
    operation_id="get_study_by_id",
)
async def get_study_by_id(
    study_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_STUDY).filter(TBL_STUDY.id == study_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Study not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Study",
        "message": "Data retrieved successfully",
        "data"   : study_response(item),
        "error"  : {},
    }
