from core.db_session import get_db
from core.api.user.views import get_current_user
from core.upload_utils import delete_cloudinary_image
import math
from typing import cast
from main import app
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from modules.project.models import TBL_PROJECT
from modules.project.schemas import *

@app.post(
    "/create_project",
    tags=["Project"],
    status_code=201,
    operation_id="create_project",
    dependencies=[Depends(get_current_user)],
)
async def create_project(
    project: ProjectModel = Depends(ProjectModel.form),
    db      : Session        = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Persist the image (if provided)
    image_filename: str | None = None
    if project.image and project.image.filename:
        image_filename = save_image(project.image)

    # 3. Insert the new record
    new_item = TBL_PROJECT(
        id          = new_id,
        name        = project.name,
        description = project.description,
        duration    = project.duration,
        role        = project.role,
        platform    = project.platform,
        challenge   = project.challenge,
        project_url = project.project_url,
        image       = image_filename,
        active      = project.active
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    data = project_response(new_item)

    return {
        "ok"     : True,
        "status" : 201,
        "title"  : "Project",
        "message": "Data created successfully",
        "data"   : data,
        "error"  : {},
    }


@app.get(
    "/get_project",
    tags=["Project"],
    operation_id="get_project",
    dependencies=[Depends(get_current_user)],
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


@app.get(
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


@app.put(
    "/update_project/{project_id}",
    tags         = ["Project"],
    operation_id = "update_project",
    dependencies = [Depends(get_current_user)],
)
async def update_project(
    project_id: str,
    project   : ProjectModel = Depends(ProjectModel.form),
    db         : Session        = Depends(get_db),
):
    item = db.query(TBL_PROJECT).filter(TBL_PROJECT.id == project_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Project not found",
    )
    setattr(item, "name", project.name)
    setattr(item, "description", project.description)
    setattr(item, "duration", project.duration)
    setattr(item, "role", project.role)
    setattr(item, "platform", project.platform)
    setattr(item, "challenge", project.challenge)
    setattr(item, "project_url", project.project_url)
    setattr(item, "active", project.active)
    if project.image and project.image.filename:
        old_image = cast(str | None, getattr(item, "image", None))
        setattr(item, "image", save_image(project.image))
        delete_cloudinary_image(old_image)

    db.commit()
    db.refresh(item)
    
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Project",
        "message": "Data updated successfully",
        "data"   : project_response(item),
        "error"  : {},
    }


@app.delete(
    "/delete_project/{project_id}",
    tags         = ["Project"],
    operation_id = "delete_project",
    dependencies = [Depends(get_current_user)],
)
async def delete_project(
    project_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_PROJECT).filter(TBL_PROJECT.id == project_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Project not found",
        )

    data = project_response(item)
    image = cast(str | None, getattr(item, "image", None))
    delete_cloudinary_image(image)
    db.delete(item)
    db.commit()

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Project",
        "message": "Data deleted successfully",
        "data"   : data,
        "error"  : {},
    }
