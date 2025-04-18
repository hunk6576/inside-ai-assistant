import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_gpt(message, system_prompt="You are a helpful assistant"):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # или gpt-4, если доступен
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ Ошибка при обращении к OpenAI:", e)
        return "❌ Не удалось получить ответ от ИИ. Попробуй позже."
