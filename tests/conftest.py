import pytest
from unittest.mock import MagicMock, patch


# Фикстура для подмены подключения к PostgreSQL
@pytest.fixture
def mock_psycopg2():
    with patch("psycopg2.connect") as mock_connect:
        # Создаем цепочку: Connection -> Cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # Настраиваем, чтобы connect() возвращал фейковый connection
        mock_connect.return_value = mock_conn
        # А connection.cursor() возвращал фейковый курсор
        mock_conn.cursor.return_value = mock_cursor
        
        # Возвращаем курсор и соединение в тест, чтобы мы могли проверять их
        yield {
            "connect": mock_connect,
            "conn": mock_conn,
            "cursor": mock_cursor
        }

# Пример фикстуры с тестовыми данными
@pytest.fixture
def sample_data():
    return {"PS5": {"title": "PlayStation 5", "price": "20000", "old_price": 21000},
        "PS5_new_price": {"title": "PlayStation 5", "price": "19000", "old_price": 20000},
        "price_increased": "📈", "price_decreased": "📉"}


