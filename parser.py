import requests
from bs4 import BeautifulSoup


PLAY_UA = "https://playua.net/"

def parse_one_article_playua(article):
    return article.select_one(".short-article__info__title").text.strip()


def parse_news_playua():
    text = requests.get(
        PLAY_UA, 
        headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"}).content
    soup = BeautifulSoup(text, "html.parser")
    articles = soup.select(".short-article")
    return [parse_one_article_playua(article) for article in articles]
