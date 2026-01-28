from product_parser import get_product_price
from database import save_to_db
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
    expected_sql = """INSERT INTO PRODUCTS (title, price)
        VALUES (%s, %s)
        ON CONFLICT (title)
        DO UPDATE SET price = EXCLUDED.price
        """
    expected_data = [("PlayStation 5", "20000")]
    mock_cursor.executemany.assert_called_once_with(expected_sql, expected_data)
    # Убеждаемся, что была команда commit
    assert mock_conn.commit.called
    assert mock_conn.close.called