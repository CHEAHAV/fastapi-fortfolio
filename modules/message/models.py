
from sqlalchemy import Boolean, Column, String, Text
from core.db import Base

class TBL_MESSAGE(Base):
    __tablename__ = "tbl_message"

    id         = Column(String(64), primary_key = True, index = True)
    first_name = Column(String(255))
    last_name  = Column(String(255))
    email      = Column(String(255))
    subject    = Column(String(255))
    message    = Column(Text)
    active     = Column(Boolean, default = True, nullable= False)
