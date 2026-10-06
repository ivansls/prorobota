from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from database.session import Base
class LeadStatus(str, Enum):
    NEW="new"; CONTACTED="contacted"; CONSULTATION_BOOKED="consultation_booked"; CONSULTATION_COMPLETED="consultation_completed"; WAITING_PAYMENT="waiting_payment"; PAID="paid"; ONBOARDING="onboarding"; ACTIVE_CLIENT="active_client"; PROGRAM_COMPLETED="program_completed"; REJECTED="rejected"
class Lead(Base):
    __tablename__="leads"
    id: Mapped[int]=mapped_column(primary_key=True)
    user_id: Mapped[int]=mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    manager_id: Mapped[int|None]=mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    status: Mapped[LeadStatus]=mapped_column(SAEnum(LeadStatus), default=LeadStatus.NEW, index=True)
    goal: Mapped[str|None]=mapped_column(Text)
    experience: Mapped[str|None]=mapped_column(Text)
    desired_position: Mapped[str|None]=mapped_column(Text)
    comment: Mapped[str|None]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
