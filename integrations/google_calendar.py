import asyncio, logging
from datetime import datetime, timedelta, timezone
from config import settings
log=logging.getLogger(__name__)
SCOPES=["https://www.googleapis.com/auth/calendar"]
def _service():
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    c=Credentials.from_service_account_file(settings.google_service_account_file,scopes=SCOPES)
    return build("calendar","v3",credentials=c,cache_discovery=False)
def _busy(calendar_id,time_min,time_max):
    s=_service(); body={"timeMin":time_min.isoformat(),"timeMax":time_max.isoformat(),"items":[{"id":calendar_id}]}
    return s.freebusy().query(body=body).execute().get("calendars",{}).get(calendar_id,{}).get("busy",[])
def _create(calendar_id,start,end,summary,description):
    s=_service(); ev={"summary":summary,"description":description,"start":{"dateTime":start.isoformat(),"timeZone":settings.google_calendar_timezone},"end":{"dateTime":end.isoformat(),"timeZone":settings.google_calendar_timezone},"conferenceData":{"createRequest":{"requestId":f"prorobota-{int(start.timestamp()*1000)}","conferenceSolutionKey":{"type":"hangoutsMeet"}}}}
    return s.events().insert(calendarId=calendar_id,body=ev,conferenceDataVersion=1,sendUpdates="all").execute()
def _delete(calendar_id,event_id): _service().events().delete(calendarId=calendar_id,eventId=event_id,sendUpdates="all").execute()
def _update(calendar_id,event_id,start,end):
    s=_service(); ev=s.events().get(calendarId=calendar_id,eventId=event_id).execute(); ev["start"]={"dateTime":start.isoformat(),"timeZone":settings.google_calendar_timezone}; ev["end"]={"dateTime":end.isoformat(),"timeZone":settings.google_calendar_timezone}; return s.events().update(calendarId=calendar_id,eventId=event_id,body=ev,sendUpdates="all").execute()
async def busy(calendar_id,start,end): return await asyncio.to_thread(_busy,calendar_id,start,end)
async def create_event(calendar_id,start,end,summary,description): return await asyncio.to_thread(_create,calendar_id,start,end,summary,description)
async def delete_event(calendar_id,event_id): return await asyncio.to_thread(_delete,calendar_id,event_id)
async def update_event(calendar_id,event_id,start,end): return await asyncio.to_thread(_update,calendar_id,event_id,start,end)
def event_meet_url(event):
    return event.get("hangoutLink") or next((e.get("uri") for e in event.get("conferenceData",{}).get("entryPoints",[]) if e.get("entryPointType")=="video"),None)
