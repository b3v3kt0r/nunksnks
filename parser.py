from datetime import datetime
import requests
from bs4 import BeautifulSoup


PLAY_UA = "https://playua.net/"
STEAM_SALES = "https://steambase.io/sales"


def fetch_html(url):
    text = requests.get(
        url, 
        headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"}).content
    soup = BeautifulSoup(text, "html.parser")
    return soup


def parse_one_article_playua(article):
    return article.select_one(".short-article__info__title").text.strip()


def parse_news_playua():
    soup = fetch_html(PLAY_UA)

    articles = soup.select(".short-article")
    return [parse_one_article_playua(article) for article in articles]


def parse_steam_sale_date():
    soup = fetch_html(STEAM_SALES)

    name = soup.select_one("a.text-green-400").text
    date = soup.select_one("p strong:nth-of-type(2)").text
    date_obj = datetime.strptime(date, "%m/%d/%Y")
    norm_date = date_obj.strftime("%d/%m/%Y")
    check_sale = soup.select_one("p.text-2xl").text

    if "is the next" in check_sale:
        return f"{name}\nDate of start: {norm_date}"
    else:
        return f"{name}\nDate of end: {norm_date}"
