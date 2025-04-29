
import os
import pandas as pd
import openai
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import Message
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
openai.api_key = OPENAI_API_KEY

# Загрузка базы товаров
df = pd.read_csv("products.csv")

# Функция поиска по товарам
def search_products(query: str):
    matches = df[df['name'].str.contains(query, case=False, na=False)]
    return matches

# Формирование промпта для GPT
def format_prompt(user_query: str, products: pd.DataFrame) -> str:
    base = f"Пользователь спрашивает: '{user_query}'.\nВот список товаров, найденных в базе:\n"
    if products.empty:
        return base + "Ничего не найдено. Ответь вежливо, что товара нет."

    for _, row in products.iterrows():
        base += f"- {row['name']}: {row['description']} (Ссылка: {row['link']})\n"

    base += "\nСформулируй профессиональный ответ от имени консультанта по оптовым продажам. Не придумывай ничего лишнего."
    return base

# GPT-запрос
async def ask_gpt(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ты деловой, вежливый Telegram-бот-консультант."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=400
    )
    return response["choices"][0]["message"]["content"]

@dp.message_handler(commands=["start"])
async def start(msg: Message):
    await msg.answer("Здравствуйте! Я ваш консультант по продукции Avalonica. Напишите название товара или ваш вопрос.")

@dp.message_handler()
async def handle_message(msg: Message):
    query = msg.text.strip()
    matches = search_products(query)
    prompt = format_prompt(query, matches)
    reply = await ask_gpt(prompt)
    await msg.answer(reply)

if __name__ == "__main__":
    executor.start_polling(dp)
