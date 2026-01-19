import requests
from bs4 import BeautifulSoup
import cloudscraper


def get_product_price(url):
    try:
        scrapper = cloudscraper.create_scraper()
        response = scrapper.get(url)
        if response.status_code == 200:
            print("Доступ разрешен")
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
        


if __name__ == "__main__":
    test_url = "https://rozetka.com.ua/ua/consoles/c80020/page=2/"
    data = get_product_price(test_url)
    print(data)