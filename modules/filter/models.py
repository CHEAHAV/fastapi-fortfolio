from core.db import Base
from sqlalchemy import Column, String, Boolean

class TBL_FILTER(Base):
    __tablename__ = "tbl_filter"

    id          = Column(String(64), primary_key = True, index = True)
    name        = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)