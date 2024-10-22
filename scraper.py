import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

def scrape_quotes():
    quotes = []

    for page in range(1, 11):  # Pages 1 to 10
        url = f"http://quotes.toscrape.com/page/{page}/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        for quote in soup.find_all('div', class_='quote'):
            text = quote.find('span', class_='text').get_text()
            author = quote.find('small', class_='author').get_text()
            tags = [tag.get_text()
                    for tag in quote.find_all('a', class_='tag')]
            quotes.append({
                'text': text,
                'author': author,
                'tags': tags
            })

    return quotes


def save_to_mongo(quotes):
    client = MongoClient('mongodb://localhost:27017/')
    db = client.quotes_db
    collection = db.quotes
    collection.insert_many(quotes)


if __name__ == "__main__":
    quotes = scrape_quotes()
    save_to_mongo(quotes)
    print("Quotes saved to MongoDB.")
