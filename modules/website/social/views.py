import math
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from core.api.user.views import get_current_user
from core.db_session import get_db
from main import website
from modules.social.models import TBL_SOCIAL
from modules.social.schemas import social_response


@website.get(
    "/get_social",
    tags=["Social"],
    operation_id="get_social",
)
async def get_social(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_SOCIAL).filter(TBL_SOCIAL.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_SOCIAL.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [social_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Social',
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
    "/get_social/{social_id}",
    tags=["social"],
    operation_id="get_social_by_id",
    dependencies=[Depends(get_current_user)],
)
async def get_social_by_id(
    social_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_SOCIAL).filter(TBL_SOCIAL.id == social_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Social not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Social",
        "message": "Data retrieved successfully",
        "data"   : social_response(item),
        "error"  : {},
    }
