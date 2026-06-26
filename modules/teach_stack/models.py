from sqlalchemy import Boolean, Column, String
from core.db import Base


class TBL_TEACH_STACK(Base):

    __tablename__ = "tbl_teach_stack"

    id          = Column(String(64), primary_key = True, index = True)
    name_left   = Column(String(255))
    image_left  = Column(String(255))
    name_right  = Column(String(255))
    image_right = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)