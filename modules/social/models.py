from sqlalchemy import Boolean, Column, String, Text
from core.db import Base

class TBL_SOCIAL(Base):

    __tablename__ = "tbl_social"

    id         = Column(String(64), primary_key = True, index = True)
    name       = Column(String(255))
    icon       = Column(String(255))
    social_url = Column(Text)
    active     = Column(Boolean, default = True, nullable= False)