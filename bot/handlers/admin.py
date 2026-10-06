from aiogram import F,Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery,Message
from bot.keyboards.admin import admin_menu,lead_actions,manager_list
from bot.keyboards.common import main_menu
from config import settings
from database.models.lead import LeadStatus
from database.models.user import UserRole
from database.repositories.leads import get_recent_leads,get_lead_details,get_funnel_counts,set_manager
from database.repositories.users import get_user_by_telegram_id,get_managers,get_or_create_user
from database.session import SessionLocal
from bot.services.notifications import send_safe,notify_manager
router=Router()
def is_admin(m):return m.from_user.id in settings.admin_id_list
@router.message(Command('admin'))
@router.message(F.text=='⚙️ Админ-панель')
async def panel(m):
 if not is_admin(m):return await m.answer('⛔ Доступ запрещён.')
 await m.answer('⚙️ <b>Админ-панель</b>',reply_markup=admin_menu())
@router.callback_query(F.data=='admin:leads')
async def leads(c):
 if c.from_user.id not in settings.admin_id_list:return await c.answer('Нет доступа',show_alert=True)
 async with SessionLocal() as s: rows=await get_recent_leads(s)
 await c.message.edit_text('📋 <b>Последние заявки</b>')
 for l,u in rows: await c.message.answer(f"<b>#{l.id}</b> — {u.first_name or ''} {u.last_name or ''}\nСтатус: <b>{l.status.value}</b>\nМенеджер: {l.manager_id or '—'}",reply_markup=lead_actions(l.id))
 await c.answer()
@router.callback_query(F.data.startswith('admin:lead:'))
async def detail(c):
 if c.from_user.id not in settings.admin_id_list:return await c.answer('Нет доступа',show_alert=True)
 lid=int(c.data.split(':')[-1])
 async with SessionLocal() as s: row=await get_lead_details(s,lid)
 if not row:return await c.answer('Заявка не найдена',show_alert=True)
 l,u=row; await c.message.answer(f"📋 <b>Заявка #{l.id}</b>\n\n👤 {u.first_name or ''} {u.last_name or ''}\n🆔 <code>{u.telegram_id}</code>\n🎯 {l.goal}\n💼 {l.experience}\n🔎 {l.desired_position}\n💬 {l.comment or '—'}\n\nСтатус: <b>{l.status.value}</b>\nМенеджер: {l.manager_id or 'не назначен'}",reply_markup=lead_actions(l.id)); await c.answer()
@router.callback_query(F.data.startswith('admin:assign:'))
async def assign(c):
 if c.from_user.id not in settings.admin_id_list:return await c.answer('Нет доступа',show_alert=True)
 lid=int(c.data.split(':')[-1])
 async with SessionLocal() as s: ms=await get_managers(s)
 if not ms:return await c.answer('Нет менеджеров. Сначала /make_manager TELEGRAM_ID',show_alert=True)
 await c.message.edit_text(f'Выберите менеджера для заявки #{lid}:',reply_markup=manager_list(lid,ms)); await c.answer()
@router.callback_query(F.data.startswith('admin:setmanager:'))
async def setmanager(c):
 if c.from_user.id not in settings.admin_id_list:return await c.answer('Нет доступа',show_alert=True)
 _,_,lid,mid=c.data.split(':'); lid=int(lid); mid=int(mid)
 async with SessionLocal() as s:
  l=await set_manager(s,lid,mid); row=await get_lead_details(s,lid); manager=await get_user_by_telegram_id(s,mid)
  client=row[1]
 await notify_manager(c.bot,manager,f"👨‍💼 Вам назначена заявка <b>#{lid}</b>.\nОткройте «Кабинет менеджера» для работы с ней.")
 await send_safe(c.bot,client.telegram_id,f"👨‍💼 Вам назначен менеджер: <b>{manager.first_name or manager.username or manager.telegram_id}</b>.")
 await c.message.edit_text(f"✅ Заявка #{lid} назначена менеджеру <b>{manager.first_name or manager.username or manager.telegram_id}</b>.")
 await c.answer()
@router.callback_query(F.data=='admin:managers')
async def managers(c):
 if c.from_user.id not in settings.admin_id_list:return await c.answer('Нет доступа',show_alert=True)
 async with SessionLocal() as s: ms=await get_managers(s)
 text='👥 <b>Менеджеры</b>\n\n'+('\n'.join(f"• {m.first_name or ''} @{m.username or '—'} — calendar: {m.calendar_id or 'не задан'}" for m in ms) if ms else 'Менеджеров нет')
 await c.message.edit_text(text,reply_markup=admin_menu()); await c.answer()
@router.callback_query(F.data=='admin:funnel')
async def funnel(c):
 if c.from_user.id not in settings.admin_id_list:return await c.answer('Нет доступа',show_alert=True)
 async with SessionLocal() as s: counts=await get_funnel_counts(s)
 await c.message.edit_text('📊 <b>Воронка</b>\n\n'+ '\n'.join(f'{k}: {v}' for k,v in counts.items()),reply_markup=admin_menu()); await c.answer()
@router.message(Command('make_manager'))
async def make_manager(m):
 if not is_admin(m):return await m.answer('⛔ Доступ запрещён.')
 p=m.text.split(maxsplit=1)
 if len(p)!=2 or not p[1].isdigit():return await m.answer('Использование: /make_manager TELEGRAM_ID')
 async with SessionLocal() as s:
  u=await get_user_by_telegram_id(s,int(p[1]))
  if not u:return await m.answer('Пользователь должен сначала отправить /start.')
  u.role=UserRole.MANAGER; await s.commit()
 await m.answer(f"✅ {p[1]} назначен менеджером.")
 await send_safe(m.bot,u.telegram_id,'👨‍💼 Вам назначена роль менеджера в ПроРабота. Теперь доступен кабинет менеджера.',reply_markup=main_menu('manager'))
@router.message(Command('set_calendar'))
async def set_calendar(m):
 if not is_admin(m):return await m.answer('⛔ Доступ запрещён.')
 p=m.text.split(maxsplit=2)
 if len(p)!=3 or not p[1].isdigit():return await m.answer('Использование: /set_calendar TELEGRAM_ID CALENDAR_ID')
 async with SessionLocal() as s:
  u=await get_user_by_telegram_id(s,int(p[1]))
  if not u:return await m.answer('Пользователь не найден.')
  u.calendar_id=p[2].strip(); await s.commit()
 await m.answer('✅ Календарь менеджера сохранён.')
