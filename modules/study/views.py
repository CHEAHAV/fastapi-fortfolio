from core.db_session import get_db
from core.api.user.views import get_current_user
import math
from main import app
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from modules.study.models import TBL_STUDY
from modules.study.schemas import *

@app.post(
    "/create_study",
    tags=["Study"],
    status_code=201,
    operation_id="create_study",
    dependencies=[Depends(get_current_user)],
)
async def create_study(
    study: StudyModel = Depends(StudyModel.form),
    db      : Session        = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Insert the new record
    new_item = TBL_STUDY(
        id          = new_id,
        title       = study.title,
        sub_title   = study.sub_title,
        description = study.description,
        date        = study.date,
        active      = study.active
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    data = study_response(new_item)

    return {
        "ok"     : True,
        "status" : 201,
        "title"  : "Study",
        "message": "Data created successfully",
        "data"   : data,
        "error"  : {},
    }


@app.get(
    "/get_study",
    tags=["Study"],
    operation_id="get_study",
    dependencies=[Depends(get_current_user)],
)
async def get_study(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_STUDY).filter(TBL_STUDY.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_STUDY.name\
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


@app.get(
    "/get_study/{study_id}",
    tags=["Study"],
    operation_id="get_study_by_id",
    dependencies=[Depends(get_current_user)],
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


@app.put(
    "/update_study/{study_id}",
    tags         = ["Study"],
    operation_id = "update_study",
    dependencies = [Depends(get_current_user)],
)
async def update_study(
    study_id: str,
    study   : StudyModel = Depends(StudyModel.form),
    db         : Session        = Depends(get_db),
):
    item = db.query(TBL_STUDY).filter(TBL_STUDY.id == study_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Study not found",
    )
    setattr(item, "title", study.title)
    setattr(item, "sub_title", study.sub_title)
    setattr(item, "description", study.description)
    setattr(item, "date", study.date)
    setattr(item, "active", study.active)

    db.commit()
    db.refresh(item)
    
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Study",
        "message": "Data updated successfully",
        "data"   : study_response(item),
        "error"  : {},
    }


@app.delete(
    "/delete_study/{study_id}",
    tags         = ["Study"],
    operation_id = "delete_study",
    dependencies = [Depends(get_current_user)],
)
async def delete_study(
    study_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_STUDY).filter(TBL_STUDY.id == study_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Study not found",
        )

    data = study_response(item)
    db.delete(item)
    db.commit()

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Study",
        "message": "Data deleted successfully",
        "data"   : data,
        "error"  : {},
    }
