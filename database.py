import psycopg2
from dotenv import load_dotenv
import os
from psycopg2.extras import execute_values


load_dotenv()
db_url = os.getenv("db_url")


import psycopg2
from psycopg2.extras import execute_values

def save_to_db(data):
    try:
        connection = psycopg2.connect(db_url)
        cursor = connection.cursor()

        # 1. Создаем временную таблицу для быстрой загрузки новых данных
        cursor.execute("""
            CREATE TEMP TABLE temp_products (
                title TEXT,
                price INTEGER,
                url TEXT
            ) ON COMMIT DROP;
        """)

        # 2. Массовая вставка данных во временную таблицу
        records = [(item["title"], item["price"], item["url"]) for item in data]
        insert_temp_query = "INSERT INTO temp_products (title, price, url) VALUES %s"
        execute_values(cursor, insert_temp_query, records)

        # 3. Обновляем основную таблицу products и получаем ID только тех товаров, 
        # у которых цена изменилась или которых еще нет в базе
        upsert_query = """
            INSERT INTO products (title, current_price, url)
            SELECT title, price, url FROM temp_products
            ON CONFLICT (title) DO UPDATE 
            SET current_price = EXCLUDED.current_price,
                url = EXCLUDED.url -- Обновляем ссылку, если она изменилась
            WHERE products.current_price IS DISTINCT FROM EXCLUDED.current_price
            RETURNING id, current_price;
        """
        cursor.execute(upsert_query)
        updated_rows = cursor.fetchall()

        # 4. Если есть изменения, массово записываем их в историю цен
        if updated_rows:
            insert_history_query = "INSERT INTO price_history (product_id, price) VALUES %s"
            execute_values(cursor, insert_history_query, updated_rows)
            print(f"Обновлено товаров и добавлено в историю: {len(updated_rows)}")
        else:
            print("Изменений цен не обнаружено.")

        connection.commit()
    except Exception as e:
        print(f"Ошибка при сохранении в БД: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection:
            cursor.close()
            connection.close()
