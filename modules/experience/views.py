from core.db_session import get_db
from core.api.user.views import get_current_user
import math
from main import app
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from modules.experience.models import TBL_EXPERIENCE
from modules.experience.schemas import *

@app.post(
    "/create_experience",
    tags=["Experience"],
    status_code=201,
    operation_id="create_experience",
    dependencies=[Depends(get_current_user)],
)
async def create_experience(
    experience: ExperienceModel = Depends(ExperienceModel.form),
    db      : Session        = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Insert the new record
    new_item = TBL_EXPERIENCE(
        id       = new_id,
        year_exp = experience.year_exp,
        project  = experience.project,
        commit   = experience.commit,
        active   = experience.active
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    data = experience_response(new_item)

    return {
        "ok"     : True,
        "status" : 201,
        "title"  : "experience",
        "message": "Data created successfully",
        "data"   : data,
        "error"  : {},
    }


@app.get(
    "/get_experience",
    tags=["Experience"],
    operation_id="get_experience",
    dependencies=[Depends(get_current_user)],
)
async def get_experience(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_EXPERIENCE).filter(TBL_EXPERIENCE.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_EXPERIENCE.id\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [experience_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'experience',
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
    "/get_experience/{experience_id}",
    tags=["Experience"],
    operation_id="get_experience_by_id",
    dependencies=[Depends(get_current_user)],
)
async def get_experience_by_id(
    experience_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_EXPERIENCE).filter(TBL_EXPERIENCE.id == experience_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "experience not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "experience",
        "message": "Data retrieved successfully",
        "data"   : experience_response(item),
        "error"  : {},
    }


@app.put(
    "/update_experience/{experience_id}",
    tags         = ["Experience"],
    operation_id = "update_experience",
    dependencies = [Depends(get_current_user)],
)
async def update_experience(
    experience_id: str,
    experience   : ExperienceModel = Depends(ExperienceModel.form),
    db         : Session        = Depends(get_db),
):
    item = db.query(TBL_EXPERIENCE).filter(TBL_EXPERIENCE.id == experience_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "experience not found",
    )
    setattr(item, "year_exp", experience.year_exp)
    setattr(item, "project", experience.project)
    setattr(item, "commit", experience.commit)
    setattr(item, "active", experience.active)

    db.commit()
    db.refresh(item)
    
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "experience",
        "message": "Data updated successfully",
        "data"   : experience_response(item),
        "error"  : {},
    }


@app.delete(
    "/delete_experience/{experience_id}",
    tags         = ["Experience"],
    operation_id = "delete_experience",
    dependencies = [Depends(get_current_user)],
)
async def delete_experience(
    experience_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_EXPERIENCE).filter(TBL_EXPERIENCE.id == experience_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "experience not found",
        )

    data = experience_response(item)
    db.delete(item)
    db.commit()

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "experience",
        "message": "Data deleted successfully",
        "data"   : data,
        "error"  : {},
    }
