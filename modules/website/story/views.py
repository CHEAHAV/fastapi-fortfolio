import math
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from core.db_session import get_db
from main import website
from modules.story.models import TBL_STORY
from modules.story.schemas import story_response

@website.get(
    "/get_story",
    tags=["Story"],
    operation_id="get_story",
)
async def get_story(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_STORY).filter(TBL_STORY.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_STORY.title\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [story_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Story',
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
    "/get_story/{story_id}",
    tags=["Story"],
    operation_id="get_story_by_id",
)
async def get_story_by_id(
    story_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_STORY).filter(TBL_STORY.id == story_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Story not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Story",
        "message": "Data retrieved successfully",
        "data"   : story_response(item),
        "error"  : {},
    }
