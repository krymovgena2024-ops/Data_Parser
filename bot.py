from aiogram import Bot, Dispatcher
from aiogram.types import Message
import asyncio, os, psycopg2
from aiogram.filters import Command
from dotenv import load_dotenv


load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
db_url = os.getenv("db_url")
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


async def check_price_changes():
    try:
        connection = psycopg2.connect(db_url)
        cursor = connection.cursor()
        # Выбираем товары, у которых последняя зафиксированная цена отличается от предыдущей записи в истории
        query = """
        SELECT 
            p.title, 
            p.url,
            ph_now.price AS new_price, 
            ph_prev.price AS old_price
        FROM price_history AS ph_now
        JOIN products p ON ph_now.product_id = p.id
        LEFT JOIN price_history AS ph_prev ON ph_prev.id = (
            SELECT id FROM price_history 
            WHERE product_id = ph_now.product_id 
              AND id < ph_now.id
            ORDER BY id DESC LIMIT 1
        )
        WHERE ph_now.id IN (SELECT MAX(id) FROM price_history GROUP BY product_id)
          AND ph_prev.price IS NOT NULL 
          AND ph_now.price != ph_prev.price;
        """
        cursor.execute(query)
        change_products = cursor.fetchall()
        #print(change_products)
        if change_products:
                report_lines = ["🔔 **Отчет об изменении цен:**\n"]
                
                for title, url, new_price, old_price in change_products:
                    diff = new_price - old_price
                    icon = "📈" if diff > 0 else "📉"
                    message = (f"{icon} **Цена изменилась!**\n" 
                            f"Товар: [{title}]({url})\n"
                            f"Старая цена: {old_price} грн.\n"
                            f"Новая цена: {new_price} грн.")
                    if len("".join(report_lines)) + len(message) >= 4050:
                        await bot.send_message(ADMIN_ID, "".join(report_lines), parse_mode="Markdown", disable_web_page_preview=True)
                        report_lines = ["...продолжение отчета:\n"]
                    report_lines.append(message)
                await bot.send_message(ADMIN_ID, "".join(report_lines), parse_mode="Markdown", disable_web_page_preview=True)
        else:
           await bot.send_message(ADMIN_ID, "🔍 Проверка завершена: новых изменений цен нет.")
            
    except Exception as e:
        print(f"Ошибка в боте: {e}")
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
    await check_price_changes()
    await bot.session.close()
    
if __name__ == "__main__":
    asyncio.run(main())
