from telegram import BotCommand
from telegram.ext import ApplicationBuilder
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

COMMANDS = [
    BotCommand("start", "Запустить бота"),
    # BotCommand("settings", "Настроить время"),  — удалено
]

async def set_commands():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    await app.bot.set_my_commands(COMMANDS)
    print("✅ Команды обновлены")

if __name__ == "__main__":
    import asyncio
    asyncio.run(set_commands())
