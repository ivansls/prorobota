from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, Text, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from database.session import Base
class AppointmentStatus(str, Enum): BOOKED="booked"; CANCELLED="cancelled"; COMPLETED="completed"
class Appointment(Base):
    __tablename__="appointments"
    __table_args__=(UniqueConstraint("manager_id","start_at","status", name="uq_active_manager_slot"),)
    id: Mapped[int]=mapped_column(primary_key=True)
    lead_id: Mapped[int]=mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int]=mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    manager_id: Mapped[int]=mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    start_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), index=True)
    end_at: Mapped[datetime]=mapped_column(DateTime(timezone=True))
    google_event_id: Mapped[str|None]=mapped_column(String(512), nullable=True)
    meet_url: Mapped[str|None]=mapped_column(String(1024), nullable=True)
    status: Mapped[AppointmentStatus]=mapped_column(SAEnum(AppointmentStatus), default=AppointmentStatus.BOOKED, index=True)
    reminder_24_sent: Mapped[bool]=mapped_column(default=False)
    reminder_1_sent: Mapped[bool]=mapped_column(default=False)
    notes: Mapped[str|None]=mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
