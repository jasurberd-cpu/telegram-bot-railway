import os
from telegram.ext import Application, CommandHandler

TOKEN = os.getenv("8424980579:AAG6eLYnl09eINSol_kUlmEdp4uyk1Oh54o")

async def start(update, context):
    await update.message.reply_text("✅ Бот работает на Render!")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
print("🚀 Бот запускается...")
app.run_polling()
