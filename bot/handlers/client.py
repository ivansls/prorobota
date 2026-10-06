from aiogram import F,Router
from aiogram.types import CallbackQuery,Message
from bot.keyboards.common import main_menu
from database.models.user import UserRole
from database.models.lead import LeadStatus
from database.repositories.users import get_or_create_user
from database.repositories.leads import get_lead_by_user_id,set_status
from database.repositories.payments import create_stub_payment
from database.repositories.learning import modules,tasks,complete_task
from database.session import SessionLocal
router=Router()
@router.message(F.text=='💳 Оплата')
async def payment(m):
 async with SessionLocal() as s:
  u=await get_or_create_user(s,m.from_user); l=await get_lead_by_user_id(s,u.id)
 if not l:return await m.answer('Заявка не найдена.')
 if l.status not in (LeadStatus.WAITING_PAYMENT,LeadStatus.CONSULTATION_COMPLETED):return await m.answer('Оплата пока недоступна на текущем этапе.')
 await m.answer('💳 <b>Тестовая оплата</b>\n\nЭто заглушка оплаты: деньги реально не списываются. Нажмите кнопку для имитации успешной оплаты.',reply_markup=__import__('aiogram').types.InlineKeyboardMarkup(inline_keyboard=[[__import__('aiogram').types.InlineKeyboardButton(text='✅ Оплатить (тест)',callback_data='payment:test')]]))
@router.callback_query(F.data=='payment:test')
async def testpay(c):
 async with SessionLocal() as s:
  u=await get_or_create_user(s,c.from_user); l=await get_lead_by_user_id(s,u.id)
  await create_stub_payment(s,l.id,u.id); l.status=LeadStatus.ONBOARDING; u.role=UserRole.CLIENT; await s.commit()
 await c.message.edit_text('✅ Тестовая оплата успешна.\n\nВы переведены в онбординг клиента.'); await c.message.answer('Теперь вам доступно обучение и личный кабинет.', reply_markup=main_menu('client')); await c.answer()
@router.message(F.text=='👤 Мой кабинет')
async def cabinet(m):
 async with SessionLocal() as s:
  u=await get_or_create_user(s,m.from_user); l=await get_lead_by_user_id(s,u.id)
 await m.answer(f"👤 <b>Кабинет</b>\n\nРоль: {u.role.value}\nСтатус программы: {l.status.value if l else '—'}")
@router.message(F.text=='📚 Обучение')
async def learning(m):
 async with SessionLocal() as s:
  u=await get_or_create_user(s,m.from_user); mods=await modules(s)
 if not mods:return await m.answer('📚 Модули пока не добавлены.')
 from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup
 await m.answer('📚 <b>Модули программы</b>',reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=x.title,callback_data=f'learn:module:{x.id}')] for x in mods]))
@router.callback_query(F.data.startswith('learn:module:'))
async def module(c):
 mid=int(c.data.split(':')[-1])
 async with SessionLocal() as s: ts=await tasks(s,mid)
 from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup
 if not ts:return await c.answer('Заданий пока нет',show_alert=True)
 await c.message.edit_text('📝 <b>Задания</b>',reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t.title,callback_data=f'learn:task:{t.id}')] for t in ts])); await c.answer()
@router.callback_query(F.data.startswith('learn:task:'))
async def task(c):
 tid=int(c.data.split(':')[-1])
 async with SessionLocal() as s:
  u=await get_or_create_user(s,c.from_user); from database.models.learning import Task; t=await s.get(Task,tid)
 if not t:return await c.answer('Не найдено',show_alert=True)
 from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup
 await c.message.edit_text(f"📝 <b>{t.title}</b>\n\n{t.description or ''}\n\n{t.material_url or ''}",reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ Задание выполнено',callback_data=f'learn:done:{tid}')]])); await c.answer()
@router.callback_query(F.data.startswith('learn:done:'))
async def done(c):
 tid=int(c.data.split(':')[-1])
 async with SessionLocal() as s:
  u=await get_or_create_user(s,c.from_user); await complete_task(s,u.id,tid)
 await c.message.edit_text('✅ Задание отмечено выполненным.'); await c.answer()
