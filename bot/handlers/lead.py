from aiogram import F,Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.keyboards.common import cancel_keyboard,main_menu
from bot.states.lead import LeadForm
from bot.services.notifications import notify_new_lead
from config import settings
from database.models.user import UserRole
from database.repositories.leads import create_lead,get_lead_by_user_id
from database.repositories.users import get_manager_with_least_leads,get_or_create_user
from database.session import SessionLocal
from integrations.google_sheets import append_lead
router=Router()
@router.message(F.text=="📝 Оставить заявку")
async def start_lead(m,state):
 async with SessionLocal() as s: u=await get_or_create_user(s,m.from_user); ex=await get_lead_by_user_id(s,u.id)
 if ex: return await m.answer(f"У вас уже есть заявка <b>#{ex.id}</b>.\nСтатус: <b>{ex.status.value}</b>")
 await state.set_state(LeadForm.goal); await m.answer("📝 <b>Шаг 1 из 4</b>\n\nКакая у вас главная цель?",reply_markup=cancel_keyboard())
@router.message(LeadForm.goal)
async def goal(m,state):
 if await cancel(m,state):return
 await state.update_data(goal=m.text.strip()); await state.set_state(LeadForm.experience); await m.answer("💼 <b>Шаг 2 из 4</b>\n\nРасскажите о вашем опыте.")
@router.message(LeadForm.experience)
async def exp(m,state):
 if await cancel(m,state):return
 await state.update_data(experience=m.text.strip()); await state.set_state(LeadForm.desired_position); await m.answer("🔎 <b>Шаг 3 из 4</b>\n\nКакие вакансии или должности вас интересуют?")
@router.message(LeadForm.desired_position)
async def pos(m,state):
 if await cancel(m,state):return
 await state.update_data(desired_position=m.text.strip()); await state.set_state(LeadForm.comment); await m.answer("💬 <b>Шаг 4 из 4</b>\n\nДополнительные пожелания? Можно написать «нет».")
@router.message(LeadForm.comment)
async def comment(m,state):
 if await cancel(m,state):return
 d=await state.get_data()
 async with SessionLocal() as s:
  u=await get_or_create_user(s,m.from_user); manager=await get_manager_with_least_leads(s)
  lead=await create_lead(s,user_id=u.id,manager_id=manager.id if manager else None,goal=d['goal'],experience=d['experience'],desired_position=d['desired_position'],comment=m.text.strip())
 await append_lead(lead,u,manager); await notify_new_lead(m.bot,lead,u,manager,settings.admin_id_list); await state.clear()
 await m.answer(f"✅ <b>Заявка #{lead.id} принята!</b>\n\nСтатус: <b>{lead.status.value}</b>",reply_markup=main_menu(u.role.value))
@router.message(F.text=="📋 Моя заявка")
async def mine(m):
 async with SessionLocal() as s:
  u=await get_or_create_user(s,m.from_user); l=await get_lead_by_user_id(s,u.id)
 if not l:return await m.answer("У вас пока нет заявки.")
 await m.answer(f"📋 <b>Заявка #{l.id}</b>\n\n🎯 {l.goal}\n💼 {l.experience}\n🔎 {l.desired_position}\n💬 {l.comment or '—'}\n\nСтатус: <b>{l.status.value}</b>\nМенеджер: {'назначен' if l.manager_id else 'не назначен'}")
async def cancel(m,state):
 if m.text=="❌ Отмена": await state.clear(); await m.answer("Заявка отменена.",reply_markup=main_menu("lead")); return True
 return False
