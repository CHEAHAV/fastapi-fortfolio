import math

from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from modules.contact_me.models import TBL_CONTACT_ME
from core.db_session import get_db
from main import website
from modules.contact_me.schemas import contact_me_response

@website.get(
    "/get_contact_me",
    tags=["Contact Me"],
    operation_id="get_contact_me",
)
async def get_contact_me(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_CONTACT_ME).filter(TBL_CONTACT_ME.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_CONTACT_ME.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [contact_me_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'contact_me',
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
    "/get_contact_me/{contact_me_id}",
    tags=["Contact Me"],
    operation_id="get_contact_me_by_id",
)
async def get_contact_me_by_id(
    contact_me_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_CONTACT_ME).filter(TBL_CONTACT_ME.id == contact_me_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "contact_me not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "contact_me",
        "message": "Data retrieved successfully",
        "data"   : contact_me_response(item),
        "error"  : {},
    }
