from sqlalchemy import Column, String, Boolean, Integer, Text
from sqlalchemy.orm import relationship

from core.db import Base


class TBL_MODULE(Base):
    __tablename__ = "tbl_module"
    id       = Column(String(55), primary_key= True, unique=True)
    name     = Column(String(150))
    name_lc  = Column(String(150))
    url      = Column(String(255))
    icon     = Column(Text)
    model    = Column(String(255))
    ordering = Column(Integer)
    active   = Column(Boolean)

    sub_modules = relationship(
        "TBL_SUB_MODULE",
        back_populates="module",
        lazy="selectin",
    )
