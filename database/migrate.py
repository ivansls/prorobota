from sqlalchemy import text
from database.session import engine, Base
from database.models import all_models

async def migrate_legacy_schema():
    # Create all new tables first.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # The first MVP made one lead per user. The full workflow allows repeat leads.
        await conn.execute(text("ALTER TABLE leads DROP CONSTRAINT IF EXISTS leads_user_id_key"))
        # Add manager calendar to an existing users table.
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS calendar_id VARCHAR(512)"))
        # PostgreSQL enum values used by the old MVP.
        enum_values = [
            'CONSULTATION_BOOKED','CONSULTATION_COMPLETED','WAITING_PAYMENT',
            'PAID','ONBOARDING','ACTIVE_CLIENT','PROGRAM_COMPLETED'
        ]
        for value in enum_values:
            await conn.execute(text(f"ALTER TYPE leadstatus ADD VALUE IF NOT EXISTS '{value}'"))
