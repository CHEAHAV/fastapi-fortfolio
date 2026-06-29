from core.db_session import get_db
from core.api.user.views import get_current_user
from core.upload_utils import delete_cloudinary_icon
import math
from typing import cast
from main import app
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from modules.story.models import TBL_STORY
from modules.story.schemas import *

@app.post(
    "/create_story",
    tags=["Story"],
    status_code=201,
    operation_id="create_story",
    dependencies=[Depends(get_current_user)],
)
async def create_story(
    story: StoryModel = Depends(StoryModel.form),
    db      : Session        = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Persist the icon (if provided)
    icon_filename: str | None = None
    if story.icon and story.icon.filename:
        icon_filename = save_icon(story.icon)

    # 3. Insert the new record
    new_item = TBL_STORY(
        id          = new_id,
        title       = story.title,
        description = story.description,
        icon_name   = story.icon_name,
        icon        = icon_filename,
        active      = story.active
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    data = story_response(new_item)

    return {
        "ok"     : True,
        "status" : 201,
        "title"  : "Story",
        "message": "Data created successfully",
        "data"   : data,
        "error"  : {},
    }


@app.get(
    "/get_story",
    tags=["Story"],
    operation_id="get_story",
    dependencies=[Depends(get_current_user)],
)
async def get_story(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_STORY).filter(TBL_STORY.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_STORY.name\
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


@app.get(
    "/get_story/{story_id}",
    tags=["Story"],
    operation_id="get_story_by_id",
    dependencies=[Depends(get_current_user)],
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


@app.put(
    "/update_story/{story_id}",
    tags         = ["Story"],
    operation_id = "update_story",
    dependencies = [Depends(get_current_user)],
)
async def update_story(
    story_id: str,
    story   : StoryModel = Depends(StoryModel.form),
    db         : Session        = Depends(get_db),
):
    item = db.query(TBL_STORY).filter(TBL_STORY.id == story_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Story not found",
    )
    setattr(item, "title", story.title)
    setattr(item, "description", story.description)
    setattr(item, "icon_name", story.icon_name)
    setattr(item, "active", story.active)
    if story.icon and story.icon.filename:
        old_icon = cast(str | None, getattr(item, "icon", None))
        setattr(item, "icon", save_icon(story.icon))
        delete_cloudinary_icon(old_icon)

    db.commit()
    db.refresh(item)
    
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Story",
        "message": "Data updated successfully",
        "data"   : story_response(item),
        "error"  : {},
    }


@app.delete(
    "/delete_story/{story_id}",
    tags         = ["Story"],
    operation_id = "delete_story",
    dependencies = [Depends(get_current_user)],
)
async def delete_story(
    story_id: str,
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_STORY).filter(TBL_STORY.id == story_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Story not found",
        )

    data = story_response(item)
    icon = cast(str | None, getattr(item, "icon", None))
    delete_cloudinary_icon(icon)
    db.delete(item)
    db.commit()

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Story",
        "message": "Data deleted successfully",
        "data"   : data,
        "error"  : {},
    }
