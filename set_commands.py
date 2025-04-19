import os
from dotenv import load_dotenv
from telegram import BotCommand
from telegram.ext import ApplicationBuilder

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

COMMANDS = [
    BotCommand("start", "Запустить бота"),
    BotCommand("settings", "Настроить время напоминаний")
]

async def set_bot_commands():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    await app.bot.set_my_commands(COMMANDS)
    print("✅ Команды успешно установлены!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(set_bot_commands())
