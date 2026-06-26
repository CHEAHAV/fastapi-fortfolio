import math
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from core.api.user.views import get_current_user
from core.db_session import get_db
from main import website
from modules.skill.models import TBL_SKILL
from modules.skill.schemas import skill_response


@website.get(
    "/get_skill",
    tags=["Skill"],
    operation_id="get_skill",
)
async def get_skill(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_SKILL).filter(TBL_SKILL.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_SKILL.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [skill_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Skill',
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
    "/get_skill/{skill_id}",
    tags=["skill"],
    operation_id="get_skill_by_id",
    dependencies=[Depends(get_current_user)],
)
async def get_skill_by_id(
    skill_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_SKILL).filter(TBL_SKILL.id == skill_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Skill not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Skill",
        "message": "Data retrieved successfully",
        "data"   : skill_response(item),
        "error"  : {},
    }
