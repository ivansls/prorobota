from datetime import datetime, timezone
from sqlalchemy import select
from database.models.appointment import Appointment, AppointmentStatus
async def get_active_for_lead(session,lead_id): return (await session.execute(select(Appointment).where(Appointment.lead_id==lead_id,Appointment.status==AppointmentStatus.BOOKED).order_by(Appointment.start_at.desc()).limit(1))).scalar_one_or_none()
async def get_user_active(session,user_id): return (await session.execute(select(Appointment).where(Appointment.user_id==user_id,Appointment.status==AppointmentStatus.BOOKED,Appointment.start_at>datetime.now(timezone.utc)).order_by(Appointment.start_at).limit(1))).scalar_one_or_none()
async def get_manager_active_between(session,manager_id,start,end):
    return (await session.execute(select(Appointment).where(Appointment.manager_id==manager_id,Appointment.status==AppointmentStatus.BOOKED,Appointment.start_at<end,Appointment.end_at>start))).scalars().all()
