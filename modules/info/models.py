from sqlalchemy import Column, Text, String, Boolean
from core.db import Base

class TBL_INFO(Base):
    __tablename__ = "tbl_info"

    id          = Column(String(64), primary_key = True, index = True)
    name        = Column(String(255))
    description = Column(Text)
    image       = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)
