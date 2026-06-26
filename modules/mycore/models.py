from sqlalchemy import Boolean, Column, String, Text
from core.db import Base

class TBL_MY_CORE(Base):

    __tablename__ = "tbl_my_core"

    id          = Column(String(64), primary_key = True, index = True)
    name        = Column(String(255))
    description = Column(Text)
    image       = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)