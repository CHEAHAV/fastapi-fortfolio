from sqlalchemy import Boolean, ForeignKey, String, Column

from core.db import Base


class TBL_USER(Base):
    __tablename__ = "tbl_user"

    id         = Column(String(55), primary_key=True, unique=True)
    username   = Column(String(100), nullable=False, unique=True, index=True)
    email      = Column(String(255), nullable=True, unique=True, index=True)
    first_name = Column(String(100), nullable=True)
    last_name  = Column(String(100), nullable=True)
    phone      = Column(String(50), nullable=True)
    password   = Column(String(255), nullable=False)
    photo      = Column(String(500), nullable=True)
    role_id    = Column(String(55), ForeignKey("tbl_role.id"), nullable=True)
    is_active  = Column(Boolean, default=True)
