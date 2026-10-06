import asyncio
from datetime import datetime,timezone,timedelta
from aiogram import Bot
from sqlalchemy import select
from database.models.appointment import Appointment,AppointmentStatus
from database.models.user import User
from database.models.lead import Lead
from database.session import SessionLocal
async def run_reminders(bot:Bot):
 while True:
  try:
   now=datetime.now(timezone.utc)
   async with SessionLocal() as s:
    rows=(await s.execute(select(Appointment,User,Lead).join(User,User.id==Appointment.user_id).join(Lead,Lead.id==Appointment.lead_id).where(Appointment.status==AppointmentStatus.BOOKED))).all()
    for ap,u,l in rows:
     delta=ap.start_at.astimezone(timezone.utc)-now
     if timedelta(hours=23,minutes=30)<=delta<=timedelta(hours=24,minutes=30) and not ap.reminder_24_sent:
      await bot.send_message(u.telegram_id,f'⏰ Напоминание: консультация завтра в {ap.start_at.astimezone().strftime("%H:%M")}.\n🎥 {ap.meet_url or "ссылка в календаре"}'); ap.reminder_24_sent=True
     if timedelta(minutes=30)<=delta<=timedelta(minutes=90) and not ap.reminder_1_sent:
      await bot.send_message(u.telegram_id,f'⏰ Напоминание: консультация через 1 час.\n🎥 {ap.meet_url or "ссылка в календаре"}'); ap.reminder_1_sent=True
    await s.commit()
  except Exception: pass
  await asyncio.sleep(60)
