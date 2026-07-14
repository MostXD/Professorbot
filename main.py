import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler, 
                          CallbackQueryHandler, ContextTypes, filters)

TOKEN = "8979345890:AAF30vdWHXNe7Z1yxeKtXI2taF1h_QcDXUg"
DATA_FILE = "data.json"

CATEGORIES = {
    "Бизнес и Юрис": ["Юрист", "Адвокат", "Нотариус", "Бухгалтер", "Аудитор", "Менеджер", "Аналитик", "Трейдер", "Риелтор", "Логист"],
    "Медицина и Психология": ["Психолог", "Врач", "Стоматолог", "Массажист", "Ветеринар", "Косметолог", "Фармацевт", "Лаборант", "Подолог", "Биолог"],
    "Интим и Мода": ["Эскорт-модель", "Стриптизер", "Модель (Adult)", "Мастер по имиджу", "Парикмахер", "Визажист", "Стилист", "Фотограф", "Дизайнер", "Швея"],
    "IT и Творчество": ["Программист", "Системный администратор", "Тестировщик", "Верстальщик", "SEO-специалист", "Таргетолог", "СММ-менеджер", "Художник", "Музыкант", "Актер"]
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

user_jobs = load_data()

async def show_jobs(update, context):
    text = "📋 **Список занятых профессий:**\n"
    for uid, data in user_jobs.items():
        text += f"{data['job']} — {data['name']}\n"
    
    # Кнопка «Устроиться» в общем списке
    keyboard = [[InlineKeyboardButton("💼 Устроиться", callback_data="cats")]]
    await update.message.reply_text(text or "Все свободно!", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update, context):
    query = update.callback_query
    data = query.data
    uid = str(query.from_user.id)
    await query.answer()

    if data == "cats":
        kb = [[InlineKeyboardButton(c, callback_data=f"cat_{c}")] for c in CATEGORIES.keys()]
        kb.append([InlineKeyboardButton("« Назад", callback_data="back_main")])
        await query.edit_message_text("Выберите категорию:", reply_markup=InlineKeyboardMarkup(kb))
    
    elif data == "back_main":
        # Возвращаем в начальное меню устройства
        kb = [[InlineKeyboardButton("💼 Выбрать профессию", callback_data="cats")]]
        await query.edit_message_text("Меню устройства на работу:", reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("cat_"):
        cat = data.split("_")[1]
        kb = [[InlineKeyboardButton(j, callback_data=f"take_{j}")] for j in CATEGORIES[cat]]
        kb.append([InlineKeyboardButton("« Назад", callback_data="cats")])
        await query.edit_message_text(f"Профессии в {cat}:", reply_markup=InlineKeyboardMarkup(kb))
    
    elif data.startswith("take_"):
        job = data.split("_")[1]
        user_jobs[uid] = {"name": query.from_user.full_name, "job": job}
        save_data(user_jobs)
        await query.edit_message_text(f"✅ Вы устроились на: {job}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("jobs", show_jobs))
    app.add_handler(MessageHandler(filters.Regex('(?i)^Профессии$'), show_jobs))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
