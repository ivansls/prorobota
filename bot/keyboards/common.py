from aiogram.types import KeyboardButton,ReplyKeyboardMarkup
def main_menu(role):
    rows=[]
    if role in ("lead","client"):
        rows += [[KeyboardButton(text="📝 Оставить заявку")],[KeyboardButton(text="📋 Моя заявка")],[KeyboardButton(text="📅 Записаться на консультацию")],[KeyboardButton(text="📅 Моя встреча")],[KeyboardButton(text="💳 Оплата")]]
    if role=="client": rows += [[KeyboardButton(text="📚 Обучение")],[KeyboardButton(text="👤 Мой кабинет")]]
    if role in ("manager","admin"): rows += [[KeyboardButton(text="👨‍💼 Кабинет менеджера")]]
    if role=="admin": rows += [[KeyboardButton(text="⚙️ Админ-панель")]]
    return ReplyKeyboardMarkup(keyboard=rows,resize_keyboard=True)
def cancel_keyboard(): return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Отмена")]],resize_keyboard=True)
