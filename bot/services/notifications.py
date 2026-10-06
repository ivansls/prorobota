from aiogram import Bot
async def send_safe(bot,telegram_id,text,**kwargs):
    try: await bot.send_message(telegram_id,text,**kwargs)
    except Exception: pass
async def notify_new_lead(bot,lead,user,manager,admin_ids):
    text=f"🆕 <b>Новая заявка #{lead.id}</b>\n\n👤 {user.first_name or ''} {user.last_name or ''}\n@{user.username or 'нет'}\n🎯 {lead.goal}\n💼 {lead.experience}\n🔎 {lead.desired_position}\n💬 {lead.comment or '—'}\n\n👨‍💼 Менеджер: {manager.first_name if manager else 'не назначен'}"
    for tid in admin_ids:
        await send_safe(bot,tid,text)
    if manager:
        from bot.keyboards.common import main_menu
        await send_safe(bot,manager.telegram_id,text,reply_markup=main_menu("manager"))
async def notify_manager(bot,manager,text):
 from bot.keyboards.common import main_menu
 await send_safe(bot,manager.telegram_id,text,reply_markup=main_menu("manager"))
