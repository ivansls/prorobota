from aiogram import F,Router
from aiogram.types import CallbackQuery,Message
from bot.keyboards.admin import manager_lead_actions,status_keyboard
from bot.keyboards.common import main_menu
from database.models.lead import LeadStatus
from database.repositories.users import get_or_create_user,get_user
from database.repositories.leads import get_manager_leads,get_lead_details,set_status
from database.session import SessionLocal
from bot.services.notifications import send_safe
router=Router()
STATUS_LABELS={LeadStatus.NEW:'🆕 Новая',LeadStatus.CONTACTED:'📞 Контакт установлен',LeadStatus.CONSULTATION_COMPLETED:'✅ Консультация проведена',LeadStatus.WAITING_PAYMENT:'💳 Ожидает оплаты',LeadStatus.PAID:'💰 Оплачено',LeadStatus.ONBOARDING:'🚀 Онбординг',LeadStatus.ACTIVE_CLIENT:'🟢 Активный клиент',LeadStatus.PROGRAM_COMPLETED:'🏁 Программа завершена',LeadStatus.REJECTED:'❌ Отказ'}
@router.message(F.text=="👨‍💼 Кабинет менеджера")
async def panel(m):
 async with SessionLocal() as s:u=await get_or_create_user(s,m.from_user)
 if u.role.value not in ('manager','admin'):return await m.answer('Доступ запрещён.')
 async with SessionLocal() as s:
  rows=await get_manager_leads(s,u.id)
 if not rows:return await m.answer('📭 Назначенных заявок нет.',reply_markup=main_menu(u.role.value))
 for l,client in rows:
  await m.answer(f"<b>#{l.id}</b> {client.first_name or ''} {client.last_name or ''}\nСтатус: <b>{l.status.value}</b>",reply_markup=manager_lead_actions(l.id))
@router.callback_query(F.data.startswith('manager:lead:'))
async def detail(c):
 lid=int(c.data.split(':')[-1])
 async with SessionLocal() as s:
  u=await get_or_create_user(s,c.from_user); row=await get_lead_details(s,lid)
 if not row:return await c.answer('Не найдено',show_alert=True)
 l,client=row
 if u.role.value=='manager' and l.manager_id!=u.id:return await c.answer('Заявка не назначена вам',show_alert=True)
 statuses=[(STATUS_LABELS[x],x.value) for x in [LeadStatus.CONTACTED,LeadStatus.CONSULTATION_COMPLETED,LeadStatus.WAITING_PAYMENT,LeadStatus.REJECTED]]
 await c.message.answer(f"📋 <b>Заявка #{l.id}</b>\n\n👤 {client.first_name or ''} {client.last_name or ''}\n🆔 {client.telegram_id}\n🎯 {l.goal}\n💼 {l.experience}\n🔎 {l.desired_position}\n💬 {l.comment or '—'}\n\nСтатус: <b>{l.status.value}</b>",reply_markup=status_keyboard(l.id,statuses)); await c.answer()
@router.callback_query(F.data.startswith('manager:status:'))
async def status(c):
 parts=c.data.split(':'); lid=int(parts[2]); new=LeadStatus(parts[3])
 async with SessionLocal() as s:
  u=await get_or_create_user(s,c.from_user); row=await get_lead_details(s,lid)
  if not row:return await c.answer('Нет заявки',show_alert=True)
  l,client=row
  if u.role.value=='manager' and l.manager_id!=u.id:return await c.answer('Нет доступа',show_alert=True)
  await set_status(s,lid,new)
 await send_safe(c.bot,client.telegram_id,f"🔔 Статус вашей заявки #{lid} изменён: <b>{new.value}</b>")
 await c.message.edit_text(f"✅ Статус заявки #{lid}: <b>{new.value}</b>"); await c.answer()
