from sqlalchemy  import Boolean, Column, String, Text
from core.db import Base

class TBL_STORY(Base):

    __tablename__ = "tbl_story"

    id          = Column(String(64), primary_key = True, index = True)
    title       = Column(String(255))
    description = Column(Text)
    icon_name   = Column(String(255))
    icon        = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)