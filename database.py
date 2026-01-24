import psycopg2


def save_to_db(data):
    try:
        connection = psycopg2.connect(
            user = "postgres",
            password = "3587",
            host = "127.0.0.1",
            port = "5432",
            database = "postgres"

        )
        cursor = connection.cursor()
        insert_query = """INSERT INTO PRODUCTS (title, price)
        VALUES (%s, %s)
        ON CONFLICT (title)
        DO UPDATE SET price = EXCLUDED.price
        """
        records_to_insert = [(item["title"], item["price"]) for item in data]
        print (records_to_insert)
        cursor.executemany(insert_query, records_to_insert)
        connection.commit()
        print(f"Обработано: {len(records_to_insert)} товаров")
    except Exception as e:
        print(e)
    finally:
        if connection:
            cursor.close()
            connection.close()
