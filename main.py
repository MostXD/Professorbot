from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler, 
                          CallbackQueryHandler, ContextTypes, ConversationHandler, filters)

# Состояния для диалога
WAITING_FOR_JOB = 1
# База данных
user_jobs = {} 

async def show_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📋 **Список занятых профессий:**\n\n"
    if not user_jobs:
        text += "Все свободны!"
    else:
        for uid, data in user_jobs.items():
            text += f"{data['name']}: {data['job']}\n"
    await update.message.reply_text(text, parse_mode='Markdown')

async def my_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    current_job = user_jobs.get(user.id, {}).get("job", "Безработный")
    text = f"👤 {user.full_name}: {current_job}"
    
    keyboard = []
    if current_job == "Безработный":
        keyboard.append([InlineKeyboardButton("💼 Устроиться на работу", callback_data="start_join")])
    else:
        keyboard.append([InlineKeyboardButton("🚫 Уволиться", callback_data="quit")])
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def start_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Введите название вашей будущей профессии:")
    return WAITING_FOR_JOB

async def save_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    job_name = update.message.text
    
    # Проверка на занятость профессии
    for uid, data in user_jobs.items():
        if data['job'].lower() == job_name.lower():
            await update.message.reply_text("❌ Эта профессия уже занята!")
            return ConversationHandler.END
            
    user_jobs[user.id] = {"name": user.full_name, "job": job_name}
    await update.message.reply_text(f"✅ Поздравляю! Вы теперь: {job_name}")
    return ConversationHandler.END

async def quit_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()
    
    if user.id in user_jobs:
        del user_jobs[user.id]
        await query.edit_message_text("👋 Вы уволились с работы.")
    else:
        await query.edit_message_text("🤷‍♂️ У вас нет работы.")
    return ConversationHandler.END

# Настройка бота с вашим токеном
app = ApplicationBuilder().token("8979345890:AAF30vdWHXNe7Z1yxeKtXI2taF1h_QcDXUg").build()

conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_join, pattern="start_join"), 
                  CallbackQueryHandler(quit_job, pattern="quit")],
    states={WAITING_FOR_JOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_job)]},
    fallbacks=[]
)

app.add_handler(CommandHandler("профессии", show_jobs))
app.add_handler(CommandHandler("моя_профессия", my_job))
app.add_handler(conv_handler)

print("Бот запущен...")
app.run_polling()
