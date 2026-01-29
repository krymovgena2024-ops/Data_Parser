import psycopg2
from dotenv import load_dotenv
import os
from psycopg2.extras import execute_values


load_dotenv()
DB_CONFIG = os.getenv("DB_CONFIG")


def save_to_db(data):
    try:
        connection = psycopg2.connect(DB_CONFIG)
        cursor = connection.cursor()
        insert_query = """INSERT INTO products (title, price)
        VALUES (%s, %s)
        ON CONFLICT (title)
        DO UPDATE SET 
        old_price = products.price,
        price = EXCLUDED.price
        WHERE products.price != EXCLUDED.price;
        """
        records_to_insert = [(item["title"], item["price"]) for item in data]
        print (records_to_insert)
        execute_values(cursor, insert_query, page_size=1000)
        #cursor.executemany(insert_query, records_to_insert)
        connection.commit()
        print(f"Обработано: {len(records_to_insert)} товаров")
    except Exception as e:
        print(e)
    finally:
        if connection:
            cursor.close()
            connection.close()
