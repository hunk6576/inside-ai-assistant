import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

async def ask_gpt(prompt, system_prompt=None):
    try:
        print(f"\n[GPT] 🔹 Входящий prompt: {prompt}")
        print(f"[GPT] 🔸 System prompt: {system_prompt}")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )

        reply = response.choices[0].message.content.strip()
        print(f"[GPT] ✅ Ответ: {reply}")
        return reply

    except Exception as e:
        print(f"[GPT] ❌ Ошибка: {e}")
        return "Произошла ошибка при обращении к ИИ 😢"
