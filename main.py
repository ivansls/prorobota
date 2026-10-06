import asyncio,logging
from aiogram import Bot,Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from bot.handlers.start import router as start_router
from bot.handlers.lead import router as lead_router
from bot.handlers.admin import router as admin_router
from bot.handlers.manager import router as manager_router
from bot.handlers.booking import router as booking_router
from bot.handlers.client import router as client_router
from config import settings
from database.migrate import migrate_legacy_schema
from scheduler.worker import run_reminders
logging.basicConfig(level=logging.INFO,format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
async def seed():
 from database.models.learning import Module,Task
 from database.session import SessionLocal
 from sqlalchemy import select
 async with SessionLocal() as s:
  if not (await s.execute(select(Module).limit(1))).scalar_one_or_none():
   m=Module(title='Модуль 1. Старт',description='Вводный модуль',position=1); s.add(m); await s.flush(); s.add(Task(module_id=m.id,title='Знакомство с программой',description='Изучите материалы и отметьте задание выполненным.',position=1)); await s.commit()
async def main():
 await migrate_legacy_schema(); await seed()
 bot=Bot(token=settings.bot_token,default=DefaultBotProperties(parse_mode=ParseMode.HTML)); storage=RedisStorage(Redis.from_url(settings.redis_url)); dp=Dispatcher(storage=storage)
 for r in [start_router,lead_router,booking_router,client_router,manager_router,admin_router]:dp.include_router(r)
 asyncio.create_task(run_reminders(bot)); logging.info('Prorobota bot started'); await dp.start_polling(bot)
if __name__=='__main__':asyncio.run(main())
