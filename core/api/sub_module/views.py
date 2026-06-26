import math
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from core.api.sub_module.models import TBL_SUB_MODULE
from core.api.sub_module.schemas import *
from core.api.user.views import get_current_user
from core.db_session import get_db
from main import app

@app.post(
    "/create_sub_module",
    tags=["Sub Module"],
    status_code=201,
    operation_id="create_sub_module",
    dependencies=[Depends(get_current_user)],
)
async def create_sub_module(
    sub_module : SubModuleModels = Depends(SubModuleModels.form),
    db     : Session      = Depends(get_db),
):
    new_id = generate_id(db)

    new_item = TBL_SUB_MODULE(
        id        = new_id,
        module_id = sub_module.module_id,
        name      = sub_module.name,
        name_lc   = sub_module.name_lc,
        url       = sub_module.url,
        icon      = sub_module.icon,
        model     = sub_module.model,
        ordering  = sub_module.ordering,
        active    = sub_module.active,

    )
    db.add(new_item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sub module ID already exists or module_id is invalid. Please try again.",
        ) from exc
    db.refresh(new_item)

    data = sub_module_response(new_item)

    return{
        "ok"    : True,
        "status": 201,
        "title" : "sub_module",
        "data"  : data,
        "error" : {},
    }



@app.get(
    "/get_sub_module",
    tags=["Sub Module"],
    operation_id="get_sub_module",
    dependencies=[Depends(get_current_user)],
)
async def get_sub_module(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = (
        db.query(TBL_SUB_MODULE)
        .options(selectinload(TBL_SUB_MODULE.module))
        .filter(TBL_SUB_MODULE.active == True)
    )

    total   = base_query.count()
    results = base_query.order_by(TBL_SUB_MODULE.ordering\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [sub_module_response(c, include_module=True) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'sub_module',
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
    "/get_sub_module/{sub_module_id}",
    tags=["Sub Module"],
    operation_id="get_sub_module_by_id",
    dependencies=[Depends(get_current_user)],
)
async def get_sub_module_by_id(
    sub_module_id: str,
    db         : Session = Depends(get_db),
):
    item = (
        db.query(TBL_SUB_MODULE)
        .options(selectinload(TBL_SUB_MODULE.module))
        .filter(TBL_SUB_MODULE.id == sub_module_id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "sub_module not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "sub_module",
        "message": "Data retrieved successfully",
        "data"   : sub_module_response(item, include_module=True),
        "error"  : {},
    }


@app.put(
    "/update_sub_module/{sub_module_id}",
    tags         = ["Sub Module"],
    operation_id = "update_sub_module",
    dependencies = [Depends(get_current_user)],
)
async def update_sub_module(
    sub_module_id: str,
    sub_module   : SubModuleModels = Depends(SubModuleModels.form),
    db         : Session        = Depends(get_db),
):
    item = db.query(TBL_SUB_MODULE).filter(TBL_SUB_MODULE.id == sub_module_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "sub_module not found",
    )
    setattr(item, "module_id", sub_module.module_id)
    setattr(item, "name", sub_module.name)
    setattr(item, "name_lc", sub_module.name_lc)
    setattr(item, "url", sub_module.url)
    setattr(item, "icon", sub_module.icon)
    setattr(item, "model", sub_module.model)
    setattr(item, "ordering", sub_module.ordering)
    setattr(item, "active", sub_module.active)

    db.commit()
    db.refresh(item)
    
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "sub_module",
        "message": "Data updated successfully",
        "data"   : sub_module_response(item),
        "error"  : {},
    }


@app.delete(
    "/delete_sub_module/{sub_module_id}",
    tags         = ["Sub Module"],
    operation_id = "delete_sub_module",
    dependencies = [Depends(get_current_user)],
)
async def delete_sub_module(
    sub_module_id: str,
    db       : Session = Depends(get_db),
):
    item = db.query(TBL_SUB_MODULE).filter(TBL_SUB_MODULE.id == sub_module_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "sub_module not found",
        )

    data = sub_module_response(item)
    db.delete(item)
    db.commit()

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "sub_module",
        "message": "Data deleted successfully",
        "data"   : data,
        "error"  : {},
    }
