from aiogram import Bot, Dispatcher
from aiogram.types import Message
import psycopg2
import asyncio
from aiogram.filters import Command
from dotenv import load_dotenv
import os


load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
DB_CONFIG = os.getenv("DB_CONFIG")
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


async def check_price_changes():
    try:
        connection = psycopg2.connect(DB_CONFIG)
        cursor = connection.cursor()
        query = "SELECT title, price, old_price FROM products WHERE old_price != price"
        cursor.execute(query)
        change_products = cursor.fetchall()
        print(change_products)
        if change_products:
            for title, new_price, old in change_products:
                diff = new_price - old
                icon = "📈" if diff > 0 else "📉"
                message = (f"{icon} **Цена изменилась!**\n" 
                           f"Товар: {title}\n"
                           f"Старая цена: {old}\n"
                           f"Новая цена: {new_price}")
                await bot.send_message(ADMIN_ID, message, parse_mode="Markdown")
            cursor.execute("UPDATE products SET old_price = price WHERE old_price != price")
            connection.commit()
            
    except Exception as e:
        print(f"Ошибка {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_name = message.from_user.first_name
    welcome_text = f"Привет {user_name}!"
    await message.answer(welcome_text, parse_mode="Markdown")


async def main():
    #await dp.start_polling(bot)
    await check_price_changes()
    await bot.session.close()
    
if __name__ == "__main__":
    asyncio.run(main())
