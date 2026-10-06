from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from database.session import Base
class Module(Base):
    __tablename__="modules"
    id: Mapped[int]=mapped_column(primary_key=True); title: Mapped[str]=mapped_column(String(255)); description: Mapped[str|None]=mapped_column(Text); position: Mapped[int]=mapped_column(Integer, default=0); is_active: Mapped[bool]=mapped_column(Boolean, default=True)
class Task(Base):
    __tablename__="tasks"
    id: Mapped[int]=mapped_column(primary_key=True); module_id: Mapped[int]=mapped_column(ForeignKey("modules.id", ondelete="CASCADE")); title: Mapped[str]=mapped_column(String(255)); description: Mapped[str|None]=mapped_column(Text); material_url: Mapped[str|None]=mapped_column(Text); position: Mapped[int]=mapped_column(Integer, default=0)
class TaskProgress(Base):
    __tablename__="task_progress"
    __table_args__=(UniqueConstraint("user_id","task_id", name="uq_task_progress"),)
    id: Mapped[int]=mapped_column(primary_key=True); user_id: Mapped[int]=mapped_column(ForeignKey("users.id", ondelete="CASCADE")); task_id: Mapped[int]=mapped_column(ForeignKey("tasks.id", ondelete="CASCADE")); completed: Mapped[bool]=mapped_column(Boolean, default=False); completed_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True), nullable=True)
