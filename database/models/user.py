from datetime import datetime
from enum import Enum
from sqlalchemy import BigInteger, Boolean, DateTime, Enum as SAEnum, String, func
from sqlalchemy.orm import Mapped, mapped_column
from database.session import Base
class UserRole(str, Enum):
    LEAD="lead"; CLIENT="client"; MANAGER="manager"; ADMIN="admin"
class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(primary_key=True)
    telegram_id: Mapped[int]=mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str|None]=mapped_column(String(255))
    first_name: Mapped[str|None]=mapped_column(String(255))
    last_name: Mapped[str|None]=mapped_column(String(255))
    phone: Mapped[str|None]=mapped_column(String(50))
    role: Mapped[UserRole]=mapped_column(SAEnum(UserRole), default=UserRole.LEAD, index=True)
    is_active: Mapped[bool]=mapped_column(Boolean, default=True)
    calendar_id: Mapped[str|None]=mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now())
