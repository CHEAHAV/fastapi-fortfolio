from sqlalchemy import Boolean, Column, String
from core.db import Base

class TBL_EXPERIENCE(Base):

    __tablename__ = "tbl_experience"

    id       = Column(String(64), primary_key = True, index = True)
    year_exp = Column(String(50))
    project  = Column(String(50))
    commit   = Column(String(50))
    active   = Column(Boolean, default = True, nullable= False)