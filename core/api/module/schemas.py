from typing import Any
from fastapi import Form, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.api.module.models import TBL_MODULE
from core.prefix_id import generate_prefixed_id


class ModuleSchemas(BaseModel):
    name    : str
    name_lc : str
    url     : str
    icon    : str | None = None
    model   : str
    ordering: int
    active  : bool

class ModuleModels(ModuleSchemas):
    @classmethod
    def form(
        cls,
        name     : str  = Form(..., examples= [""]),
        name_lc  : str  = Form(..., examples=[""]),
        url      : str  = Form(..., examples=[""]),
        icon     : str  = Form(None, examples=[""]),
        model    : str  = Form(..., examples=[""]),
        ordering : int  = Form(..., examples=[""]),
        active   : bool = True,

    ):
        return cls(
            name     = name,
            name_lc  = name_lc,
            url      = url,
            icon     = icon,
            model    = model,
            ordering = ordering,
            active   = active,
        )

def generate_id(db: Session)-> str:
    result = generate_prefixed_id(db, [
        TBL_MODULE
    ], "MOD")
    if result is None:
        raise HTTPException(status_code=500, detail= "Failed to generate a unique ID")
    return result

def module_response(item : Any, include_sub_modules: bool = True)-> dict[str, Any]:
    data = {
        "id"      : getattr(item, "id"),
        "name"    : getattr(item, "name"),
        "name_lc" : getattr(item, "name_lc"),
        "url"     : getattr(item, "url"),
        "icon"    : getattr(item, "icon"),
        "model"   : getattr(item, "model"),
        "ordering": getattr(item, "ordering"),
        "active"  : getattr(item, "active"),
    }

    if include_sub_modules:
        from core.api.sub_module.schemas import sub_module_response

        sub_modules = getattr(item, "sub_modules", []) or []
        data["sub_modules"] = [
            sub_module_response(sub_module, include_module=False)
            for sub_module in sub_modules
        ]

    return data
