from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.keyboards.common import main_menu
from database.repositories.users import get_or_create_user
from database.session import SessionLocal
router=Router()
@router.message(CommandStart())
async def start(message:Message):
 async with SessionLocal() as s: u=await get_or_create_user(s,message.from_user)
 await message.answer("👋 Добро пожаловать в <b>ПроРабота</b>!\n\nВыберите нужное действие в меню.",reply_markup=main_menu(u.role.value))
