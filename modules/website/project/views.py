import math
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from core.api.user.views import get_current_user
from core.db_session import get_db
from main import website
from modules.project.models import TBL_PROJECT
from modules.project.schemas import project_response

@website.get(
    "/get_project",
    tags=["Project"],
    operation_id="get_project",
)
async def get_project(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_PROJECT).filter(TBL_PROJECT.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_PROJECT.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [project_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Project',
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
    "/get_project/{project_id}",
    tags=["Project"],
    operation_id="get_project_by_id",
    dependencies=[Depends(get_current_user)],
)
async def get_project_by_id(
    project_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_PROJECT).filter(TBL_PROJECT.id == project_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Project not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Project",
        "message": "Data retrieved successfully",
        "data"   : project_response(item),
        "error"  : {},
    }
