from sqlalchemy import Boolean, Column, String, Text
from core.db import Base

class TBL_CONTACT_ME(Base):

    __tablename__ = "tbl_contact_me"
    
    id          = Column(String(64), primary_key= True, unique=True)
    name        = Column(String(255))
    description = Column(String(255))
    icon        = Column(String(255))
    contact_url = Column(Text)
    active      = Column(Boolean, default= True, nullable= False)