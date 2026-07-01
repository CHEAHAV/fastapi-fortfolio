from core.db_session import get_db
from core.api.user.views import get_current_user
import math
from main import app
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from modules.message.models import TBL_MESSAGE
from modules.message.schemas import *

@app.get(
    "/get_message",
    tags=["Message"],
    operation_id="get_message",
    dependencies=[Depends(get_current_user)],
)
async def get_message(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_MESSAGE).filter(TBL_MESSAGE.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_MESSAGE.first_name\
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


@app.get(
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


@app.put(
    "/update_message/{message_id}",
    tags         = ["Message"],
    operation_id = "update_message",
    dependencies = [Depends(get_current_user)],
)
async def update_message(
    message_id: str,
    message   : MessageModel = Depends(MessageModel.form),
    db         : Session        = Depends(get_db),
):
    item = db.query(TBL_MESSAGE).filter(TBL_MESSAGE.id == message_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Message not found",
    )
    setattr(item, "first_name", message.first_name)
    setattr(item, "last_name", message.last_name)
    setattr(item, "email", message.email)
    setattr(item, "phone", message.phone)
    setattr(item, "subject", message.subject)
    setattr(item, "message", message.message)
    setattr(item, "active", message.active)

    db.commit()
    db.refresh(item)
    
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Message",
        "message": "Data updated successfully",
        "data"   : message_response(item),
        "error"  : {},
    }


@app.delete(
    "/delete_message/{message_id}",
    tags         = ["Message"],
    operation_id = "delete_message",
    dependencies = [Depends(get_current_user)],
)
async def delete_message(
    message_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_MESSAGE).filter(TBL_MESSAGE.id == message_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Message not found",
        )

    data = message_response(item)
    db.delete(item)
    db.commit()

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Message",
        "message": "Data deleted successfully",
        "data"   : data,
        "error"  : {},
    }
