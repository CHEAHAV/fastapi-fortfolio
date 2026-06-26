from sqlalchemy import Date, Text, Column, String, Boolean
from core.db import Base

class TBL_CERTIFICATION(Base):
    __tablename__ = "tbl_certification"

    id              = Column(String(64), primary_key = True, index = True)
    name            = Column(String(255))
    title           = Column(String(255))
    issuer          = Column(String(255))
    date_earned     = Column(Date)
    credential_id   = Column(String(255))
    certificate_url = Column(Text)
    icon            = Column(String(255))
    active          = Column(Boolean, default = True, nullable= False)