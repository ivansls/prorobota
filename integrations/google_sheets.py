import asyncio,logging
from datetime import datetime
from config import settings
log=logging.getLogger(__name__)
HEADERS=["Дата","ID заявки","Telegram ID","Username","Имя","Телефон","Цель","Опыт","Желаемая позиция","Комментарий","Менеджер Telegram ID","Статус"]
def _service():
 from google.oauth2.service_account import Credentials
 from googleapiclient.discovery import build
 c=Credentials.from_service_account_file(settings.google_service_account_file,scopes=["https://www.googleapis.com/auth/spreadsheets"]); return build("sheets","v4",credentials=c,cache_discovery=False)
def _ensure():
 s=_service(); r=f"'{settings.google_worksheet_name}'!A1:L1"; ex=s.spreadsheets().values().get(spreadsheetId=settings.google_spreadsheet_id,range=r).execute().get("values",[])
 if not ex:s.spreadsheets().values().update(spreadsheetId=settings.google_spreadsheet_id,range=r,valueInputOption="RAW",body={"values":[HEADERS]}).execute()
def _append(row): _service().spreadsheets().values().append(spreadsheetId=settings.google_spreadsheet_id,range=f"'{settings.google_worksheet_name}'!A:L",valueInputOption="USER_ENTERED",insertDataOption="INSERT_ROWS",body={"values":[row]}).execute()
async def append_lead(lead,user,manager):
 if not settings.google_sheets_enabled or not settings.google_spreadsheet_id:return
 row=[datetime.now().strftime("%Y-%m-%d %H:%M:%S"),str(lead.id),str(user.telegram_id),user.username or "",(" ".join(filter(None,[user.first_name,user.last_name]))),user.phone or "",lead.goal or "",lead.experience or "",lead.desired_position or "",lead.comment or "",str(manager.telegram_id) if manager else "",lead.status.value]
 try: await asyncio.to_thread(_ensure); await asyncio.to_thread(_append,row)
 except Exception: log.exception("Google Sheets export failed for lead %s",lead.id)
