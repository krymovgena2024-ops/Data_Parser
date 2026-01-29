import requests
from bs4 import BeautifulSoup
import cloudscraper
from database import save_to_db
import time
from concurrent.futures import ThreadPoolExecutor


def get_product_price(page):
    test_url = "https://rozetka.com.ua/ua/consoles/c80020/page="
    url = f"{test_url}{page}"
    try:
        scrapper = cloudscraper.create_scraper()
        response = scrapper.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            products = soup.find_all("article", class_="content")
            print(len(products))
            results = []
            for item in products:
                title_name = item.find("a", class_="tile-title")
                title_name = title_name.get_text(strip=True)
                product_price = item.find("div", class_="price")
                raw_price = product_price.get_text(strip=True)
                product_price = "".join(filter(str.isdigit, raw_price))
                results.append({"title": title_name, "price": product_price})
            return results
    except Exception as e:
        print(f"Ошибка: {e}")


def fast_scrapper():
    all_data = []
    with ThreadPoolExecutor() as executor:
        pages = list(range(1, 57))
        result = list(executor.map(get_product_price, pages))
    for res in result:
        all_data.extend(res)
    if all_data:
        unique_data = {item['title']: item for item in all_data}.values()
        start = time.time()
        save_to_db(unique_data)
        finish = time.time()
        print(f"Result save: {finish-start}")


if __name__ == "__main__":
    start = time.time()
    fast_scrapper()
    finish = time.time()
    print(f"Result: {finish-start}")