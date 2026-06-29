import math
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from core.db_session import get_db
from main import website
from modules.teach_stack.models import TBL_TEACH_STACK
from modules.teach_stack.schemas import teach_stack_response

@website.get(
    "/get_teach_stack",
    tags=["Teach Stack"],
    operation_id="get_teach_stack",
)
async def get_teach_stack(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_TEACH_STACK).filter(TBL_TEACH_STACK.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_TEACH_STACK.name_left\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [teach_stack_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Teack Stack',
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
    "/get_teach_stack/{teach_stack_id}",
    tags=["Teach Stack"],
    operation_id="get_teach_stack_by_id",
)
async def get_teach_stack_by_id(
    teach_stack_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_TEACH_STACK).filter(TBL_TEACH_STACK.id == teach_stack_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "teach_stack not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Teach Stack",
        "message": "Data retrieved successfully",
        "data"   : teach_stack_response(item),
        "error"  : {},
    }
