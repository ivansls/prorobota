from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.lead import Lead, LeadStatus
from database.models.user import User
async def get_lead_by_user_id(session,user_id): return (await session.execute(select(Lead).where(Lead.user_id==user_id).order_by(Lead.created_at.desc()).limit(1))).scalar_one_or_none()
async def get_lead(session,lead_id): return (await session.execute(select(Lead).where(Lead.id==lead_id))).scalar_one_or_none()
async def create_lead(session,**kw):
    lead=Lead(**kw); session.add(lead); await session.commit(); await session.refresh(lead); return lead
async def get_lead_details(session,lead_id):
    stmt=select(Lead,User).join(User,User.id==Lead.user_id).where(Lead.id==lead_id); return (await session.execute(stmt)).one_or_none()
async def get_recent_leads(session,limit=30):
    stmt=select(Lead,User).join(User,User.id==Lead.user_id).order_by(Lead.created_at.desc()).limit(limit); return (await session.execute(stmt)).all()
async def get_manager_leads(session,manager_id):
    stmt=select(Lead,User).join(User,User.id==Lead.user_id).where(Lead.manager_id==manager_id).order_by(Lead.updated_at.desc()); return (await session.execute(stmt)).all()
async def get_funnel_counts(session):
    r=await session.execute(select(Lead.status,func.count(Lead.id)).group_by(Lead.status)); return {s.value:c for s,c in r.all()}
async def set_manager(session,lead_id,manager_id):
    l=await get_lead(session,lead_id); l.manager_id=manager_id; await session.commit(); await session.refresh(l); return l
async def set_status(session,lead_id,status):
    l=await get_lead(session,lead_id); l.status=status; await session.commit(); await session.refresh(l); return l
