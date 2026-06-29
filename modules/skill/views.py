from core.db_session import get_db
from core.api.user.views import get_current_user
from core.upload_utils import delete_cloudinary_image
import math
from typing import cast
from main import app
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from modules.skill.models import TBL_SKILL
from modules.skill.schemas import *

@app.post(
    "/create_skill",
    tags=["Skill"],
    status_code=201,
    operation_id="create_skill",
    dependencies=[Depends(get_current_user)],
)
async def create_skill(
    skill: SkillModel = Depends(SkillModel.form),
    db      : Session        = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Persist the image (if provided)
    image_filename: str | None = None
    if skill.image and skill.image.filename:
        image_filename = save_image(skill.image)

    # 3. Insert the new record
    new_item = TBL_SKILL(
        id          = new_id,
        name        = skill.name,
        score       = skill.score,
        description = skill.description,
        image       = image_filename,
        active      = skill.active
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    data = skill_response(new_item)

    return {
        "ok"     : True,
        "status" : 201,
        "title"  : "Skill",
        "message": "Data created successfully",
        "data"   : data,
        "error"  : {},
    }


@app.get(
    "/get_skill",
    tags=["Skill"],
    operation_id="get_skill",
    dependencies=[Depends(get_current_user)],
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


@app.get(
    "/get_skill/{skill_id}",
    tags=["Skill"],
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


@app.put(
    "/update_skill/{skill_id}",
    tags         = ["Skill"],
    operation_id = "update_skill",
    dependencies = [Depends(get_current_user)],
)
async def update_skill(
    skill_id: str,
    skill   : SkillModel = Depends(SkillModel.form),
    db         : Session        = Depends(get_db),
):
    item = db.query(TBL_SKILL).filter(TBL_SKILL.id == skill_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Skill not found",
    )
    setattr(item, "name", skill.name)
    setattr(item, "score", skill.score)
    setattr(item, "description", skill.description)
    setattr(item, "active", skill.active)
    if skill.image and skill.image.filename: 
        setattr(item, "image", save_image(skill.image))

    db.commit()
    db.refresh(item)
    
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Skill",
        "message": "Data updated successfully",
        "data"   : skill_response(item),
        "error"  : {},
    }


@app.delete(
    "/delete_skill/{skill_id}",
    tags         = ["Skill"],
    operation_id = "delete_skill",
    dependencies = [Depends(get_current_user)],
)
async def delete_skill(
    skill_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_SKILL).filter(TBL_SKILL.id == skill_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Skill not found",
        )

    data = skill_response(item)
    image = cast(str | None, getattr(item, "image", None))
    delete_cloudinary_image(image)
    db.delete(item)
    db.commit()

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Skill",
        "message": "Data deleted successfully",
        "data"   : data,
        "error"  : {},
    }
