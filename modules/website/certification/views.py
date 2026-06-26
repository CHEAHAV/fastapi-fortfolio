import math
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from core.db_session import get_db
from main import website
from modules.certification.models import TBL_CERTIFICATION
from modules.certification.schemas import certification_response

@website.get(
    "/get_certification",
    tags=["Certification"],
    operation_id="get_certification",
)
async def get_certification(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_CERTIFICATION).filter(TBL_CERTIFICATION.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_CERTIFICATION.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [certification_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Certification',
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
    "/get_certification/{certificate_id}",
    tags=["Certification"],
    operation_id="get_certification_by_id",
)
async def get_certification_by_id(
    certificate_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_CERTIFICATION).filter(TBL_CERTIFICATION.id == certificate_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Certification not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Certification",
        "message": "Data retrieved successfully",
        "data"   : certification_response(item),
        "error"  : {},
    }
