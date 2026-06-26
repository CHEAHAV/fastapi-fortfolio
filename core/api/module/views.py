import math
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from core.api.module.models import TBL_MODULE
from core.api.module.schemas import *
from core.api.user.views import get_current_user
from core.db_session import get_db
from main import app

@app.post(
    "/create_module",
    tags=["Module"],
    status_code=201,
    operation_id="create_module",
    dependencies=[Depends(get_current_user)],
)
async def create_module(
    module : ModuleModels = Depends(ModuleModels.form),
    db     : Session      = Depends(get_db),
):
    new_id = generate_id(db)


    new_item = TBL_MODULE(
        id       = new_id,
        name     = module.name,
        name_lc  = module.name_lc,
        url      = module.url,
        icon     = module.icon,
        model    = module.model,
        ordering = module.ordering,
        active   = module.active,

    )
    db.add(new_item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Module ID already exists. Please try again.",
        ) from exc
    db.refresh(new_item)

    data = module_response(new_item)

    return{
        "ok"    : True,
        "status": 201,
        "title" : "Module",
        "data"  : data,
        "error" : {},
    }



@app.get(
    "/get_module",
    tags=["Module"],
    operation_id="get_module",
    dependencies=[Depends(get_current_user)],
)
async def get_module(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = (
        db.query(TBL_MODULE)
        .options(selectinload(TBL_MODULE.sub_modules))
        .filter(TBL_MODULE.active == True)
    )

    total   = base_query.count()
    results = base_query.order_by(TBL_MODULE.ordering\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [module_response(c) for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Module',
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
    "/get_module/{module_id}",
    tags=["Module"],
    operation_id="get_module_by_id",
    dependencies=[Depends(get_current_user)],
)
async def get_module_by_id(
    module_id: str,
    db         : Session = Depends(get_db),
):
    item = (
        db.query(TBL_MODULE)
        .options(selectinload(TBL_MODULE.sub_modules))
        .filter(TBL_MODULE.id == module_id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Module not found",
        )

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Module",
        "message": "Data retrieved successfully",
        "data"   : module_response(item),
        "error"  : {},
    }


@app.put(
    "/update_module/{module_id}",
    tags         = ["Module"],
    operation_id = "update_module",
    dependencies = [Depends(get_current_user)],
)
async def update_module(
    module_id: str,
    Module   : ModuleModels = Depends(ModuleModels.form),
    db         : Session        = Depends(get_db),
):
    item = db.query(TBL_MODULE).filter(TBL_MODULE.id == module_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Module not found",
    )
    setattr(item, "name", Module.name)
    setattr(item, "name_lc", Module.name_lc)
    setattr(item, "url", Module.url)
    setattr(item, "icon", Module.icon)
    setattr(item, "model", Module.model)
    setattr(item, "ordering", Module.ordering)
    setattr(item, "active", Module.active)

    db.commit()
    db.refresh(item)
    
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Module",
        "message": "Data updated successfully",
        "data"   : module_response(item),
        "error"  : {},
    }


@app.delete(
    "/delete_module/{module_id}",
    tags         = ["Module"],
    operation_id = "delete_module",
    dependencies = [Depends(get_current_user)],
)
async def delete_module(
    module_id: str,
    db       : Session = Depends(get_db),
):
    item = db.query(TBL_MODULE).filter(TBL_MODULE.id == module_id).first()
    if not item:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Module not found",
        )

    data = module_response(item)
    db.delete(item)
    db.commit()
    
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Module",
        "message": "Data deleted successfully",
        "data"   : data,
        "error"  : {},
    }
