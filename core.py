import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


async def ask_gpt(prompt, system_prompt=None):
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"❌ Ошибка при обращении к OpenAI: {e}")
        return f"❌ Ошибка при обращении к ИИ: {e}"
