from product_parser import get_product_price
from database import save_to_db
from bot import check_price_changes
import pytest
from unittest.mock import patch


# данные для теста
MOCK_HTML = """
<article class="content">
    <a class="tile-title">PlayStation 5</a>
    <div class="price">20 000 грн</div>
</article>
"""

def test_get_product_price_with_mocker(mocker):
    # ПЕРЕХВАТ: Мы говорим mocker заменить 'cloudscraper.create_scraper'
    mock_scraper_factory = mocker.patch('cloudscraper.create_scraper')
    # НАСТРОЙКА: Создаем цепочку ответов
    mock_scraper = mock_scraper_factory.return_value 
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = MOCK_HTML
    # Говорим, что при вызове .get() нужно вернуть наш mock_response
    mock_scraper.get.return_value = mock_response
    # Мы подменяем соединение, чтобы не подключатся к реальной базе
    mock_connect = mocker.patch('psycopg2.connect')
    mock_conn = mock_connect.return_value
    mock_cursor = mock_conn.cursor.return_value
    results = get_product_price("https://fake-rozetka.com")
    save_to_db(results)
    assert len(results) == 1
    assert results[0]["title"] == "PlayStation 5"
    assert results[0]["price"] == "20000"
    expected_sql = """INSERT INTO products (title, price)
        VALUES (%s, %s)
        ON CONFLICT (title)
        DO UPDATE SET 
        old_price = products.price,
        price = EXCLUDED.price
        WHERE products.price != EXCLUDED.price;
        """
    expected_data = [("PlayStation 5", "20000")]
    mock_cursor.executemany.assert_called_once_with(expected_sql, expected_data)
    # Убеждаемся, что была команда commit
    assert mock_conn.commit.called
    assert mock_conn.close.called

@pytest.mark.asyncio
async def test_check_price_changes(mock_psycopg2, sample_data):
    products = sample_data["PS5"]
    expected_sql = "SELECT title, price, old_price FROM products WHERE old_price != price"
    expected_sql2 = "UPDATE products SET old_price = price WHERE old_price != price"
    fake_results = [(products["title"], int(products["price"]), products["old_price"])]
    mock_psycopg2["cursor"].fetchall.return_value = fake_results
    await check_price_changes()
    mock_psycopg2["cursor"].execute.assert_any_call(expected_sql)
    mock_psycopg2["cursor"].execute.assert_any_call(expected_sql2)
    assert mock_psycopg2["conn"].commit.called
    assert mock_psycopg2["cursor"].close.called
    assert mock_psycopg2["conn"].close.called
    
