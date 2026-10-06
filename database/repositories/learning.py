from datetime import datetime, timezone
from sqlalchemy import select
from database.models.learning import Module,Task,TaskProgress
async def modules(session): return (await session.execute(select(Module).where(Module.is_active.is_(True)).order_by(Module.position))).scalars().all()
async def tasks(session,module_id): return (await session.execute(select(Task).where(Task.module_id==module_id).order_by(Task.position))).scalars().all()
async def complete_task(session,user_id,task_id):
    p=(await session.execute(select(TaskProgress).where(TaskProgress.user_id==user_id,TaskProgress.task_id==task_id))).scalar_one_or_none()
    if not p: p=TaskProgress(user_id=user_id,task_id=task_id); session.add(p)
    p.completed=True; p.completed_at=datetime.now(timezone.utc); await session.commit()
