import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler, 
                          CallbackQueryHandler, ContextTypes, filters)

TOKEN = "8979345890:AAF30vdWHXNe7Z1yxeKtXI2taF1h_QcDXUg"
DATA_FILE = "data.json"

# Список из 100 профессий, разбитый по категориям
CATEGORIES = {
    "Бизнес и Юрис": ["Юрист", "Адвокат", "Нотариус", "Бухгалтер", "Аудитор", "Менеджер", "Аналитик", "Трейдер", "Риелтор", "Логист", "Секретарь", "HR-менеджер", "Директор", "Маркетолог", "Копирайтер", "Блогер", "Риелтор", "Консультант", "Детектив", "Предприниматель", "Агент", "Страховщик", "Экономист", "Стартапер", "Брокер"],
    "Медицина и Психология": ["Психолог", "Врач", "Стоматолог", "Массажист", "Ветеринар", "Косметолог", "Фармацевт", "Лаборант", "Подолог", "Биолог", "Хирург", "Логопед", "Диетолог", "Окулист", "Психиатр", "Медбрат", "Невролог", "Кардиолог", "Педиатр", "Терапевт", "Травматолог", "Реаниматолог", "Гинеколог", "Уролог", "Эндокринолог"],
    "Интим и Мода": ["Эскорт-модель", "Стриптизер", "Модель (Adult)", "Мастер по имиджу", "Парикмахер", "Визажист", "Стилист", "Фотограф", "Дизайнер", "Швея", "Модель", "Модельер", "Тату-мастер", "Косплеер", "Мастер маникюра", "Ювелир", "Брадобрей", "Модельер-конструктор", "Дизайнер интерьера", "Флорист", "Художник", "Иллюстратор", "Декоратор", "Графический дизайнер", "Кутюрье"],
    "IT и Творчество": ["Программист", "Системный администратор", "Тестировщик", "Верстальщик", "SEO-специалист", "Таргетолог", "СММ-менеджер", "Художник", "Музыкант", "Актер", "Режиссер", "Оператор", "Звукорежиссер", "Монтажер", "Диджей", "Хореограф", "Сценарист", "Аниматор", "Писатель", "Переводчик", "Журналист", "Ученый", "Астроном", "Геолог", "Физик"]
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

# --- Логика ---

async def show_jobs(update, context):
    text = "📋 **Список занятых профессий:**\n"
    if not user_jobs:
        text += "Все свободно!"
    else:
        for uid, data in user_jobs.items():
            text += f"{data['job']} — {data['name']}\n"
    
    uid = str(update.effective_user.id)
    keyboard = [[InlineKeyboardButton("💼 Устроиться", callback_data=f"cats|{uid}")]]
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def my_job(update, context):
    user = update.effective_user
    uid = str(user.id)
    job = user_jobs.get(uid, {}).get("job", "Безработный")
    
    keyboard = []
    if job == "Безработный":
        keyboard.append([InlineKeyboardButton("💼 Выбрать профессию", callback_data=f"cats|{uid}")])
    else:
        keyboard.append([InlineKeyboardButton("🚫 Уволиться", callback_data=f"quit|{uid}")])
    
    await update.message.reply_text(f"👤 Ваша работа: {job}", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update, context):
    query = update.callback_query
    uid = str(query.from_user.id)
    data_parts = query.data.split("|")
    action = data_parts[0]
    
    # ПРОВЕРКА: Если ID пользователя не совпадает с тем, кто вызвал меню
    if len(data_parts) > 1 and data_parts[-1] != uid:
        await query.answer("❌ Это не ваше меню!", show_alert=True)
        return

    await query.answer()

    if action == "cats":
        kb = [[InlineKeyboardButton(c, callback_data=f"cat|{c}|{uid}")] for c in CATEGORIES.keys()]
        await query.edit_message_text("Выберите категорию:", reply_markup=InlineKeyboardMarkup(kb))
    
    elif action == "cat":
        cat = data_parts[1]
        kb = [[InlineKeyboardButton(j, callback_data=f"take|{j}|{uid}")] for j in CATEGORIES[cat]]
        kb.append([InlineKeyboardButton("« Назад", callback_data=f"cats|{uid}")])
        await query.edit_message_text(f"Профессии в {cat}:", reply_markup=InlineKeyboardMarkup(kb))
    
    elif action == "take":
        job = data_parts[1]
        user_jobs[uid] = {"name": query.from_user.full_name, "job": job}
        save_data(user_jobs)
        await query.edit_message_text(f"✅ Вы устроились на: {job}")
    
    elif action == "quit":
        if uid in user_jobs:
            del user_jobs[uid]
            save_data(user_jobs)
            await query.edit_message_text("👋 Вы уволились.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Команды
    app.add_handler(CommandHandler("jobs", show_jobs))
    app.add_handler(CommandHandler("myjob", my_job))
    app.add_handler(MessageHandler(filters.Regex('(?i)^Профессии$'), show_jobs))
    app.add_handler(MessageHandler(filters.Regex('(?i)^Моя профессия$'), my_job))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Бот запущен...")
    app.run_polling()
