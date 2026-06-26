from fastapi import Depends
from sqlalchemy.orm import Session

from core.db_session import get_db
from core.api.role.models import TBL_ROLE
from main import app


@app.get("/roles", tags=["Role"])
async def list_roles(db: Session = Depends(get_db)):
    roles = db.query(TBL_ROLE).order_by(TBL_ROLE.name.asc()).all()
    return {
        "ok": True,
        "status": 200,
        "title": "Role",
        "message": "Data retrieved successfully",
        "data": [
            {
                "id"          : role.id,
                "name"        : role.name,
                "name_lc"     : role.name_lc,
                "description" : role.description,
                "is_superuser": role.is_superuser,
                "is_active"   : role.is_active,
            }
            for role in roles
        ],
        "error": {},
    }
