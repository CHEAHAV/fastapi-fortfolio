import math
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from core.api.user.views import get_current_user
from core.db_session import get_db
from main import website
from modules.message.models import TBL_MESSAGE
from modules.message.schemas import message_response

@website.get(
    "/get_message",
    tags=["Message"],
    operation_id="get_message",
)
async def get_message(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_MESSAGE).filter(TBL_MESSAGE.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_MESSAGE.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [message_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Message',
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
    "/get_message/{message_id}",
    tags=["Message"],
    operation_id="get_message_by_id",
    dependencies=[Depends(get_current_user)],
)
async def get_message_by_id(
    message_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_MESSAGE).filter(TBL_MESSAGE.id == message_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Message not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Message",
        "message": "Data retrieved successfully",
        "data"   : message_response(item),
        "error"  : {},
    }

