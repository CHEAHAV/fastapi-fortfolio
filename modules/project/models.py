from sqlalchemy import Boolean, Column, String, Text
from core.db import Base

class TBL_PROJECT(Base):

    __tablename__ = "tbl_project"

    id          = Column(String(64), primary_key = True, index = True)
    name        = Column(String(255))
    description = Column(Text)
    duration    = Column(String(255))
    role        = Column(String(255))
    platform    = Column(String(255))
    challenge   = Column(Text)
    project_url = Column(Text)
    image       = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)
