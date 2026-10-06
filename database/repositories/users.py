from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings
from database.models.lead import Lead
from database.models.user import User, UserRole
async def get_or_create_user(session,tg_user):
    r=await session.execute(select(User).where(User.telegram_id==tg_user.id)); u=r.scalar_one_or_none()
    if not u:
        u=User(telegram_id=tg_user.id,username=tg_user.username,first_name=tg_user.first_name,last_name=tg_user.last_name,role=UserRole.ADMIN if tg_user.id in settings.admin_id_list else UserRole.LEAD); session.add(u)
    else:
        u.username=tg_user.username; u.first_name=tg_user.first_name; u.last_name=tg_user.last_name
        if tg_user.id in settings.admin_id_list: u.role=UserRole.ADMIN
    await session.commit(); await session.refresh(u); return u
async def get_user_by_telegram_id(session,telegram_id): return (await session.execute(select(User).where(User.telegram_id==telegram_id))).scalar_one_or_none()
async def get_user(session,user_id): return await session.get(User,user_id)
async def get_managers(session): return (await session.execute(select(User).where(User.role==UserRole.MANAGER,User.is_active.is_(True)).order_by(User.first_name))).scalars().all()
async def get_manager_with_least_leads(session):
    stmt=select(User).outerjoin(Lead,Lead.manager_id==User.id).where(User.role==UserRole.MANAGER,User.is_active.is_(True)).group_by(User.id).order_by(func.count(Lead.id)).limit(1)
    return (await session.execute(stmt)).scalar_one_or_none()
