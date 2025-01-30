import sqlite3
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("reactions.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS reactions (
                        user_id INTEGER,
                        chat_id INTEGER,
                        timestamp INTEGER,
                        count INTEGER DEFAULT 1)''')
    conn.commit()
    conn.close()

# Обработчик реакций
def reaction_handler(update: Update, context: CallbackContext):
    if update.message.reaction:
        user_id = update.message.from_user.id
        chat_id = update.message.chat_id
        timestamp = update.message.date.timestamp()
        
        conn = sqlite3.connect("reactions.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO reactions (user_id, chat_id, timestamp) VALUES (?, ?, ?)", (user_id, chat_id, timestamp))
        conn.commit()
        conn.close()

# Команда для просмотра статистики
def stats(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    period = context.args[0] if context.args else "day"
    
    conn = sqlite3.connect("reactions.db")
    cursor = conn.cursor()
    
    query = "SELECT COUNT(*) FROM reactions WHERE user_id = ? AND chat_id = ? AND timestamp >= ?"
    from datetime import datetime, timedelta
    now = datetime.utcnow().timestamp()
    if period == "week":
        time_limit = now - 7 * 86400
    else:
        time_limit = now - 86400
    
    cursor.execute(query, (user_id, chat_id, time_limit))
    count = cursor.fetchone()[0]
    conn.close()
    
    update.message.reply_text(f"Вы получили {count} реакций за {period}!")

# Главная функция запуска бота
async def main():
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(MessageHandler(filters.ALL, reaction_handler))
    app.add_handler(CommandHandler("stats", stats))
    
    init_db()
    print("Бот запущен...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())