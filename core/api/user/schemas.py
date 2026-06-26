from pydantic import BaseModel


class UserSchema(BaseModel):
    id        : str
    username  : str
    email     : str | None = None
    first_name: str | None = None
    last_name : str | None = None
    phone     : str | None = None
    photo     : str | None = None
    role_id   : str | None = None
    is_active : bool = True
