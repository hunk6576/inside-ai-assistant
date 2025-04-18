import asyncio
from core import ask_gpt

async def test():
    response = await ask_gpt("Привет, как дела?", system_prompt="Ты дружелюбный ассистент.")
    print(response)

asyncio.run(test())
