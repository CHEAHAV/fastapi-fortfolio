from sqlalchemy import Boolean, String, Column
from core.db import Base


class TBL_ROLE(Base):
    __tablename__ = "tbl_role"

    id           = Column(String(55), primary_key=True, unique=True)
    name         = Column(String(255), nullable=False)
    name_lc      = Column(String(255), nullable=True)
    description  = Column(String(500), nullable=True)
    is_superuser = Column(Boolean, default=False)
    is_active    = Column(Boolean, default=True)
