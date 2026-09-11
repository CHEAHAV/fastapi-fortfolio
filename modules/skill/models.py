from sqlalchemy import Boolean, Column, String, Text, Numeric
from core.db import Base

class TBL_SKILL(Base):

    __tablename__ = "tbl_skill"

    id          = Column(String(64), primary_key = True, index = True)
    name        = Column(String(255))
    score       = Column(Numeric(8,2))
    description = Column(Text)
    official_url = Column(String(2048), nullable=True)
    image       = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)
