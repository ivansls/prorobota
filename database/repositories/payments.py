from sqlalchemy import select
from database.models.payment import Payment,PaymentStatus
async def create_stub_payment(session,lead_id,user_id,amount=0):
    p=Payment(lead_id=lead_id,user_id=user_id,amount=amount,status=PaymentStatus.SUCCEEDED,provider_payment_id=f"TEST-{lead_id}"); session.add(p); await session.commit(); await session.refresh(p); return p
