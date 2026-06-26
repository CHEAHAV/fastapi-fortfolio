
from typing import Any
from fastapi import Form, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.api.sub_module.models import TBL_SUB_MODULE
from core.prefix_id import generate_prefixed_id


class SubModuleSchemas(BaseModel):
    module_id: str
    name     : str
    name_lc  : str
    url      : str
    icon     : str | None = None
    model    : str
    ordering : int
    active   : bool

class SubModuleModels(SubModuleSchemas):
    @classmethod
    def form(
        cls,
        module_id : str  = Form(..., examples=[""]),
        name      : str  = Form(..., examples= [""]),
        name_lc   : str  = Form(..., examples=[""]),
        url       : str  = Form(..., examples=[""]),
        icon      : str  = Form(None, examples=[""]),
        model     : str  = Form(..., examples=[""]),
        ordering  : int  = Form(..., examples=[""]),
        active    : bool = True,

    ):
        return cls(
            module_id = module_id,
            name      = name,
            name_lc   = name_lc,
            url       = url,
            icon      = icon,
            model     = model,
            ordering  = ordering,
            active    = active,
        )

def generate_id(db: Session)-> str:
    result = generate_prefixed_id(db, [
        TBL_SUB_MODULE
    ], "SMD")
    if result is None:
        raise HTTPException(status_code=500, detail= "Failed to generate a unique ID")
    return result

def sub_module_response(item : Any, include_module: bool = False)-> dict[str, Any]:
    data = {
        "id"       : getattr(item, "id"),
        "module_id": getattr(item, "module_id"),
        "name"     : getattr(item, "name"),
        "name_lc"  : getattr(item, "name_lc"),
        "url"      : getattr(item, "url"),
        "icon"     : getattr(item, "icon"),
        "model"    : getattr(item, "model"),
        "ordering" : getattr(item, "ordering"),
        "active"   : getattr(item, "active"),
    }

    if include_module:
        from core.api.module.schemas import module_response

        module = getattr(item, "module", None)
        data["module"] = module_response(module, include_sub_modules=False) if module else None

    return data
