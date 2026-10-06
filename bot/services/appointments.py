from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
from config import settings
from database.models.appointment import Appointment,AppointmentStatus
from database.models.lead import LeadStatus
from database.repositories.appointments import get_active_for_lead,get_user_active,get_manager_active_between
from integrations.google_calendar import busy,create_event,delete_event,update_event,event_meet_url
LOCAL=ZoneInfo(settings.google_calendar_timezone)
def localnow(): return datetime.now(LOCAL)
def parse_hm(v): h,m=map(int,v.split(":")); return h,m
async def available_slots(calendar_id,day):
    if not settings.google_calendar_enabled or not calendar_id:return []
    now=localnow()+timedelta(hours=settings.appointment_min_hours_before)
    sh,sm=parse_hm(settings.appointment_work_start); eh,em=parse_hm(settings.appointment_work_end)
    start=datetime(day.year,day.month,day.day,sh,sm,tzinfo=LOCAL); finish=datetime(day.year,day.month,day.day,eh,em,tzinfo=LOCAL)
    if finish<=now:return []
    busy_items=await busy(calendar_id,start,finish); ranges=[(datetime.fromisoformat(x["start"].replace("Z","+00:00")),datetime.fromisoformat(x["end"].replace("Z","+00:00"))) for x in busy_items]
    out=[]; cur=start
    while cur+timedelta(minutes=settings.appointment_duration_minutes)<=finish:
        end=cur+timedelta(minutes=settings.appointment_duration_minutes)
        if cur>=now and not any(cur<be and end>bs for bs,be in ranges): out.append(cur)
        cur += timedelta(minutes=settings.appointment_step_minutes)
    return out
async def book(session,lead,user,manager,start):
    end=start+timedelta(minutes=settings.appointment_duration_minutes)
    if start<localnow()+timedelta(hours=settings.appointment_min_hours_before): raise ValueError("Слишком поздно для записи")
    if await get_user_active(session,user.id): raise ValueError("У клиента уже есть активная запись")
    if await get_manager_active_between(session,manager.id,start,end): raise ValueError("Это время уже занято")
    calendar_id=manager.calendar_id or settings.google_calendar_id
    if not calendar_id: raise ValueError("У менеджера не настроен календарь")
    b=await busy(calendar_id,start,end)
    if b: raise ValueError("Слот уже занят в Google Calendar")
    event=await create_event(calendar_id,start,end,f"ПроРабота — консультация #{lead.id}",f"Клиент: {user.first_name or ''} {user.last_name or ''}\nTelegram ID: {user.telegram_id}\nЗаявка: #{lead.id}")
    ap=Appointment(lead_id=lead.id,user_id=user.id,manager_id=manager.id,start_at=start,end_at=end,google_event_id=event.get("id"),meet_url=event_meet_url(event)); session.add(ap); lead.status=LeadStatus.CONSULTATION_BOOKED; await session.commit(); await session.refresh(ap); return ap
async def cancel(session,ap,manager_calendar_id):
    if ap.start_at.astimezone(timezone.utc)<datetime.now(timezone.utc)+timedelta(hours=settings.appointment_min_hours_before): raise ValueError("Отмена доступна не позднее чем за 4 часа")
    if ap.google_event_id: await delete_event(manager_calendar_id,ap.google_event_id)
    ap.status=AppointmentStatus.CANCELLED; from database.models.lead import LeadStatus; lead=await session.get(__import__("database.models.lead",fromlist=["Lead"]).Lead,ap.lead_id); lead.status=LeadStatus.CONTACTED; await session.commit()
async def reschedule(session,ap,manager,start):
    if ap.start_at.astimezone(timezone.utc)<datetime.now(timezone.utc)+timedelta(hours=settings.appointment_min_hours_before): raise ValueError("Перенос доступен не позднее чем за 4 часа")
    end=start+timedelta(minutes=settings.appointment_duration_minutes); calendar_id=manager.calendar_id or settings.google_calendar_id
    if await get_manager_active_between(session,manager.id,start,end): raise ValueError("Время уже занято")
    if await busy(calendar_id,start,end): raise ValueError("Время уже занято в календаре")
    ev=await update_event(calendar_id,ap.google_event_id,start,end); ap.start_at=start; ap.end_at=end; ap.meet_url=event_meet_url(ev) or ap.meet_url; await session.commit()
