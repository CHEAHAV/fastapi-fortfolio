from pydantic import BaseModel


class RoleSchema(BaseModel):
    id: str
    name: str
    name_lc: str | None = None
    description: str | None = None
    is_superuser: bool = False
    is_active: bool = True
