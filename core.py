import os
import openai
from dotenv import load_dotenv

# Загружаем ключи из .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

async def ask_gpt(prompt, system_prompt=None):
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await openai.ChatCompletion.acreate(
            model="gpt-4-1106-preview",  # или gpt-4, если preview не доступен
            messages=messages,
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("❌ Ошибка при обращении к OpenAI:", e)
        return "Произошла ошибка при обращении к ИИ 😢"
