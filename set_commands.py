from telegram import BotCommand
from telegram.ext import ApplicationBuilder
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

commands = [
    BotCommand("start", "Перезапустить бота"),
    BotCommand("history", "Показать дневник"),
    BotCommand("talk", "Просто поболтать")
]

async def set_commands():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    await app.bot.set_my_commands(commands)
    print("✅ Команды обновлены")

if __name__ == "__main__":
    import asyncio
    asyncio.run(set_commands())
