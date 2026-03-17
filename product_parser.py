from bs4 import BeautifulSoup
import cloudscraper
from database import save_to_db
import time
from concurrent.futures import ThreadPoolExecutor


def get_product_price(page):
    test_url = "https://rozetka.com.ua/ua/mobile-phones/c80003/page="
    url = f"{test_url}{page}"
    try:
        scrapper = cloudscraper.create_scraper()
        response = scrapper.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            products = soup.find_all("article", class_="content")
            results = []
            for item in products:
                title_name = item.find("a", class_="tile-title")
                title_name = title_name.get_text(strip=True)
                product_price = item.find("div", class_="price")
                raw_price = product_price.get_text(strip=True)
                product_price = "".join(filter(str.isdigit, raw_price))
                # Ищем ссылку (тег <a>)
                link_element = item.find("a", class_="tile-title")
                if link_element:
                    title_name = link_element.get_text(strip=True)
                # Извлекаем саму ссылку из атрибута href
                product_url = link_element['href']
                results.append({"title": title_name, "price": product_price, "url": product_url})
            return results
    except Exception as e:
        print(f"Ошибка: {e}")


def fast_scrapper():
    all_data = []
    with ThreadPoolExecutor() as executor:
        pages = list(range(1, 84))
        result = list(executor.map(get_product_price, pages))
    for res in result:
        if res:
            all_data.extend(res)
    if all_data:
        unique_data = {item['title']: item for item in all_data}.values()
        start = time.time()
        save_to_db(list(unique_data))
        finish = time.time()
        print(f"Всего собрано товаров: {len(all_data)}")
        print(f"Уникальных товаров: {len(unique_data)}")
        print(f"Время сохранения: {finish-start}")
    else:
        print("Данные не собраны, сохранять нечего!")


if __name__ == "__main__":
    start = time.time()
    fast_scrapper()
    finish = time.time()
    print(f"Время парсинга: {finish-start}")