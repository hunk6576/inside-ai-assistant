import os
import json
import asyncio
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core import ask_gpt
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

JOURNAL_PATH = "journals"
USER_PATH = "users"
os.makedirs(JOURNAL_PATH, exist_ok=True)
os.makedirs(USER_PATH, exist_ok=True)

BUTTONS = [
    ["📖 Мой дневник", "💬 Поговорим"],
    ["🛠 Настройки"]
]
reply_markup = ReplyKeyboardMarkup(BUTTONS, resize_keyboard=True)
STYLE_CHOICES = ReplyKeyboardMarkup([["На ты", "На вы"]], resize_keyboard=True)

user_contexts = {}
user_schedulers = {}
scheduler = AsyncIOScheduler()

def save_user_time(user_id, morning_time=None, evening_time=None):
    user_file = f"{USER_PATH}/{user_id}.json"
    data = {}
    if os.path.exists(user_file):
        with open(user_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    if morning_time:
        data["morning_time"] = morning_time
    if evening_time:
        data["evening_time"] = evening_time
    with open(user_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def load_user_time(user_id):
    user_file = f"{USER_PATH}/{user_id}.json"
    if os.path.exists(user_file):
        with open(user_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("morning_time", "08:00"), data.get("evening_time", "21:00")
    return "08:00", "21:00"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_file = f"{USER_PATH}/{user_id}.json"

    if not os.path.exists(user_file):
        await update.message.reply_text(
            "Привет! \U0001F44B\nКак ты хочешь, чтобы я с тобой общался?",
            reply_markup=STYLE_CHOICES
        )
    else:
        await update.message.reply_text(
            "С возвращением! Готов продолжить путь к себе ✨",
            reply_markup=reply_markup
        )

async def save_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    style = update.message.text
    if style not in ["На ты", "На вы"]:
        return False

    user_id = update.effective_user.id
    user_file = f"{USER_PATH}/{user_id}.json"
    data = {"style": style}
    if os.path.exists(user_file):
        with open(user_file, "r", encoding="utf-8") as f:
            existing = json.load(f)
        data.update(existing)

    with open(user_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    await update.message.reply_text(
        f"Отлично, теперь я буду обращаться {'на ты' if style == 'На ты' else 'на вы'} \U0001F60A",
        reply_markup=reply_markup
    )
    return True

def schedule_user_messages(user_id, app):
    morning_time, evening_time = load_user_time(user_id)

    def parse_time(t):
        h, m = map(int, t.split(":"))
        return h, m

    if user_id in user_schedulers:
        job_ids = user_schedulers[user_id]
        for job_id in job_ids:
            scheduler.remove_job(job_id)

    morning_hour, morning_minute = parse_time(morning_time)
    evening_hour, evening_minute = parse_time(evening_time)

    m_job = scheduler.add_job(send_morning_message, "cron", hour=morning_hour, minute=morning_minute, args=[app, user_id])
    e_job = scheduler.add_job(send_evening_message, "cron", hour=evening_hour, minute=evening_minute, args=[app, user_id])
    user_schedulers[user_id] = [m_job.id, e_job.id]

async def send_morning_message(app, user_id):
    try:
        await app.bot.send_message(
            chat_id=user_id,
            text="☀️ Доброе утро! Запиши, с каким настроем ты хочешь войти в день. Какие мысли или планы крутятся в голове?"
        )
        user_contexts[user_id] = "🌞 Утро"
    except Exception as e:
        print(f"❌ Утро: ошибка {user_id}: {e}")

async def send_evening_message(app, user_id):
    try:
        await app.bot.send_message(chat_id=user_id, text="\U0001F319 Как прошёл день? Запиши мысли или идеи \U0001F4D3")
        user_contexts[user_id] = "\U0001F319 Вечер"
    except Exception as e:
        print(f"\u274C Вечер: ошибка {user_id}: {e}")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text.strip()

    user_file = f"{USER_PATH}/{user_id}.json"
    if not os.path.exists(user_file):
        saved = await save_style(update, context)
        if saved:
            return

    with open(user_file, "r", encoding="utf-8") as f:
        user_data = json.load(f)
        style = user_data.get("style", "На ты")

    if user_input == "\U0001F6E0 Настройки":
        context.user_data["settings_step"] = "set_morning"
        await update.message.reply_text("Во сколько тебе присылать утреннее сообщение? (например, 08:00)")
        return

    if context.user_data.get("settings_step") == "set_morning":
        if ":" not in user_input or not all(part.isdigit() for part in user_input.split(":")):
            await update.message.reply_text("\u26D4 Неверный формат. Пожалуйста, используй формат HH:MM")
            return
        save_user_time(user_id, morning_time=user_input)
        context.user_data["settings_step"] = "set_evening"
        await update.message.reply_text("А вечернее? (например, 21:00)")
        return

    if context.user_data.get("settings_step") == "set_evening":
        if ":" not in user_input or not all(part.isdigit() for part in user_input.split(":")):
            await update.message.reply_text("\u26D4 Неверный формат. Пожалуйста, используй формат HH:MM")
            return
        save_user_time(user_id, evening_time=user_input)
        context.user_data.pop("settings_step")
        schedule_user_messages(user_id, context.application)
        await update.message.reply_text("\u2705 Время напоминаний обновлено!", reply_markup=reply_markup)
        return

    if user_input == "\U0001F4D6 Мой дневник":
        path = f"{JOURNAL_PATH}/{user_id}.txt"
        if not os.path.exists(path):
            await update.message.reply_text("У тебя пока нет записей. Начни сегодня \U0001F4D3")
            return
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-5:]
        text = "".join(lines)
        await update.message.reply_text(f"\U0001F4D6 Вот последние записи:\n\n{text}")
        return

    if user_input == "\U0001F4AC Поговорим":
        await update.message.reply_text("О чём хочешь поговорить? Я рядом \U0001F64C")
        return

    if context.user_data.get("awaiting_journal") or user_id in user_contexts:
        moment = context.user_data.pop("awaiting_journal", None) or user_contexts.pop(user_id, None)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(f"{JOURNAL_PATH}/{user_id}.txt", "a", encoding="utf-8") as f:
            f.write(f"{now} [{moment}]: {user_input}\n")
        await update.message.reply_text("\u270D\ufe0f Записал. Спасибо, что поделился.")
        return
        
    prompt = (
        "Ты тёплый и внимательный ассистент по самопознанию, психологии и осознанности. Общайся на 'ты' и не выходи за рамки этих тем."
        if style == "На ты" else
        "Вы заботливый и поддерживающий ассистент по психологии, саморазвитию и осознанности. Общайтесь с уважением на 'вы'."
    )

    await update.message.chat.send_action("typing")
    reply = await ask_gpt(user_input, system_prompt=prompt)
    await update.message.reply_text(reply)
    
from telegram import BotCommand

async def set_commands(app):
    await app.bot.set_my_commands([
        BotCommand("start", "Перезапустить бота"),
        BotCommand("history", "Показать дневник"),
        BotCommand("talk", "Просто поболтать"),
        BotCommand("settings", "Настроить время напоминаний")
    ])
    
async def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    await set_commands(app)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    scheduler.start()
    await app.initialize()

    for user_id in app.user_data:
        schedule_user_messages(user_id, app)

    await app.run_polling(close_loop=False)

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    print("\u2705 Бот запущен с автонапоминаниями и настройками \U0001F557")
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    loop.run_forever()
