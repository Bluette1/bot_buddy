import requests
from bs4 import BeautifulSoup

def scrape_quotes():
    url = "http://quotes.toscrape.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    quotes = []

    for quote in soup.find_all('div', class_='quote'):
        text = quote.find('span', class_='text').get_text()
        author = quote.find('small', class_='author').get_text()
        tags = [tag.get_text() for tag in quote.find_all('a', class_='tag')]
        quotes.append({
            'text': text,
            'author': author,
            'tags': tags
        })

    return quotes

if __name__ == "__main__":
    quotes = scrape_quotes()
    for quote in quotes:
        print(f"{quote['text']} - {quote['author']}")
        print(f"Tags: {', '.join(quote['tags'])}")
        print()