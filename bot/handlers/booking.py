from datetime import date,datetime,timedelta
from aiogram import F,Router
from aiogram.types import CallbackQuery,Message,InlineKeyboardButton,InlineKeyboardMarkup
from bot.keyboards.admin import meeting_actions
from config import settings
from database.models.lead import LeadStatus
from database.repositories.leads import get_lead_by_user_id
from database.repositories.users import get_or_create_user,get_user
from database.repositories.appointments import get_user_active
from database.session import SessionLocal
from bot.services.appointments import available_slots,book,cancel,reschedule
from bot.services.notifications import send_safe
router=Router()
def days_kb(prefix='book:day:'):
 return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=(date.today()+timedelta(days=i)).strftime('%d.%m (%a)'),callback_data=f'{prefix}{(date.today()+timedelta(days=i)).isoformat()}')] for i in range(settings.appointment_days_ahead)])
def slots_kb(prefix,slots): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=x.strftime('%H:%M'),callback_data=f'{prefix}{x.isoformat()}')] for x in slots])
@router.message(F.text=='📅 Записаться на консультацию')
async def start_book(m):
 async with SessionLocal() as s:
  u=await get_or_create_user(s,m.from_user); l=await get_lead_by_user_id(s,u.id); manager=await get_user(s,l.manager_id) if l and l.manager_id else None; active=await get_user_active(s,u.id)
 if not l:return await m.answer('Сначала оставьте заявку.')
 if not manager:return await m.answer('Менеджер ещё не назначен. Запись станет доступна после назначения менеджера.')
 if l.status!=LeadStatus.CONTACTED:return await m.answer('Менеджер ещё не открыл запись. Сначала менеджер должен перевести заявку в статус «Контакт установлен».')
 if active:return await m.answer('У вас уже есть активная запись. Откройте «📅 Моя встреча».')
 await m.answer('📅 Выберите дату:',reply_markup=days_kb())
@router.callback_query(F.data.startswith('book:day:'))
async def choose_day(c):
 d=date.fromisoformat(c.data.split(':')[-1])
 async with SessionLocal() as s:
  u=await get_or_create_user(s,c.from_user); l=await get_lead_by_user_id(s,u.id); manager=await get_user(s,l.manager_id) if l and l.manager_id else None
 if not manager:return await c.answer('Менеджер не назначен',show_alert=True)
 slots=await available_slots(manager.calendar_id or settings.google_calendar_id,d)
 await c.message.edit_text(f'📅 {d.strftime("%d.%m.%Y")}\n\nВыберите свободное время:',reply_markup=slots_kb('book:slot:',slots)); await c.answer()
@router.callback_query(F.data.startswith('book:slot:'))
async def choose_slot(c):
 start=datetime.fromisoformat(c.data.split(':',2)[2])
 await c.message.edit_text(f'Вы выбрали <b>{start.strftime("%d.%m.%Y %H:%M")}</b>.\n\nПодтвердить запись?',reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ Подтвердить',callback_data=f'book:confirm:{start.isoformat()}')],[InlineKeyboardButton(text='❌ Отмена',callback_data='book:cancel')]])); await c.answer()
@router.callback_query(F.data.startswith('book:confirm:'))
async def confirm(c):
 start=datetime.fromisoformat(c.data.split(':',2)[2])
 try:
  async with SessionLocal() as s:
   u=await get_or_create_user(s,c.from_user); l=await get_lead_by_user_id(s,u.id); manager=await get_user(s,l.manager_id) if l else None
   if not l or not manager:raise ValueError('Менеджер не назначен')
   ap=await book(s,l,u,manager,start)
  await c.message.edit_text(f'✅ <b>Запись подтверждена</b>\n\n📅 {ap.start_at.strftime("%d.%m.%Y")}\n🕐 {ap.start_at.strftime("%H:%M")}–{ap.end_at.strftime("%H:%M")}\n👨‍💼 {manager.first_name or manager.username or manager.telegram_id}\n🎥 {ap.meet_url or "Ссылка в Google Calendar"}')
  await send_safe(c.bot,manager.telegram_id,f'📅 Новая консультация по заявке <b>#{l.id}</b>\nДата: {ap.start_at.strftime("%d.%m.%Y")}\nВремя: {ap.start_at.strftime("%H:%M")}\n🎥 {ap.meet_url or "ссылка в календаре"}')
 except Exception as e:return await c.answer(str(e),show_alert=True)
 await c.answer()
@router.callback_query(F.data=='book:cancel')
async def book_cancel(c): await c.message.edit_text('Запись не создана.'); await c.answer()
@router.message(F.text=='📅 Моя встреча')
async def mymeeting(m):
 async with SessionLocal() as s:u=await get_or_create_user(s,m.from_user); ap=await get_user_active(s,u.id)
 if not ap:return await m.answer('Активной записи нет.')
 await m.answer(f'📅 <b>Ваша консультация</b>\n\nДата: {ap.start_at.strftime("%d.%m.%Y")}\nВремя: {ap.start_at.strftime("%H:%M")}–{ap.end_at.strftime("%H:%M")}\n🎥 {ap.meet_url or "нет ссылки"}',reply_markup=meeting_actions())
@router.callback_query(F.data=='meeting:cancel')
async def meeting_cancel(c):
 async with SessionLocal() as s:
  u=await get_or_create_user(s,c.from_user); ap=await get_user_active(s,u.id); manager=await get_user(s,ap.manager_id) if ap else None
  if not ap:return await c.answer('Активной записи нет',show_alert=True)
  try: await cancel(s,ap,manager.calendar_id or settings.google_calendar_id)
  except Exception as e:return await c.answer(str(e),show_alert=True)
 await c.message.edit_text('❌ Запись отменена.'); await send_safe(c.bot,manager.telegram_id,f'❌ Клиент отменил консультацию по заявке <b>#{ap.lead_id}</b>.'); await c.answer()
@router.callback_query(F.data=='meeting:reschedule')
async def meeting_reschedule(c): await c.message.edit_text('📅 Выберите новую дату:',reply_markup=days_kb('res:day:')); await c.answer()
@router.callback_query(F.data.startswith('res:day:'))
async def res_day(c):
 d=date.fromisoformat(c.data.split(':')[-1])
 async with SessionLocal() as s:
  u=await get_or_create_user(s,c.from_user); ap=await get_user_active(s,u.id); manager=await get_user(s,ap.manager_id) if ap else None
 if not manager:return await c.answer('Активной записи нет',show_alert=True)
 slots=await available_slots(manager.calendar_id or settings.google_calendar_id,d); await c.message.edit_text('Выберите новое время:',reply_markup=slots_kb('res:slot:',slots)); await c.answer()
@router.callback_query(F.data.startswith('res:slot:'))
async def res_slot(c):
 start=datetime.fromisoformat(c.data.split(':',2)[2]); await c.message.edit_text(f'Перенести встречу на <b>{start.strftime("%d.%m.%Y %H:%M")}</b>?',reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ Да',callback_data=f'res:confirm:{start.isoformat()}')],[InlineKeyboardButton(text='❌ Нет',callback_data='book:cancel')]])); await c.answer()
@router.callback_query(F.data.startswith('res:confirm:'))
async def res_confirm(c):
 start=datetime.fromisoformat(c.data.split(':',2)[2])
 try:
  async with SessionLocal() as s:
   u=await get_or_create_user(s,c.from_user); ap=await get_user_active(s,u.id); manager=await get_user(s,ap.manager_id) if ap else None
   if not ap or not manager:raise ValueError('Активной записи нет')
   await reschedule(s,ap,manager,start)
  await c.message.edit_text(f'✅ Встреча перенесена на <b>{start.strftime("%d.%m.%Y %H:%M")}</b>.')
 except Exception as e:return await c.answer(str(e),show_alert=True)
 await c.answer()
