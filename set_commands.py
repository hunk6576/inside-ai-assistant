
from telegram import BotCommand
from telegram.ext import ApplicationBuilder
from config import TELEGRAM_BOT_TOKEN

async def set_menu():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    commands = [
        BotCommand("start", "Перезапустить бота"),
        BotCommand("morning", "Утренний настрой"),
        BotCommand("evening", "Записать мысли вечером"),
        BotCommand("history", "Показать дневник"),
        BotCommand("talk", "Просто поболтать")
    ]
    await app.bot.set_my_commands(commands)
    print("✅ Команды Telegram успешно установлены.")

import asyncio
asyncio.run(set_menu())
