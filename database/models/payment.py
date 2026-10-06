from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from database.session import Base
class PaymentStatus(str, Enum): PENDING="pending"; SUCCEEDED="succeeded"; FAILED="failed"
class Payment(Base):
    __tablename__="payments"
    id: Mapped[int]=mapped_column(primary_key=True); lead_id: Mapped[int]=mapped_column(ForeignKey("leads.id", ondelete="CASCADE")); user_id: Mapped[int]=mapped_column(ForeignKey("users.id", ondelete="CASCADE")); amount: Mapped[int]=mapped_column(Integer, default=0); status: Mapped[PaymentStatus]=mapped_column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING); provider_payment_id: Mapped[str|None]=mapped_column(String(255), nullable=True); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now()); updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
