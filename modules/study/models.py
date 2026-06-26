from sqlalchemy import Boolean, Column, String, Text
from core.db import Base

class TBL_STUDY(Base):

    __tablename__ = "tbl_study"

    id          = Column(String(64), primary_key = True, index = True)
    title       = Column(String(255))
    sub_title   = Column(String(255))
    description = Column(Text)
    date        = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)