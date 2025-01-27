from datetime import datetime
import html
import requests

from bs4 import BeautifulSoup


PLAY_UA = "https://playua.net/"
STEAM_SALES = "https://steambase.io/sales"
DOU_LVIV_ACTIVITIES = "https://dou.ua/calendar/city/Lviv/"


def fetch_html(url):
    text = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        },
    ).content
    soup = BeautifulSoup(text, "html.parser")
    return soup


def parse_one_article_playua(article):
    return article.select_one(".short-article__info__title").text.strip()


def parse_news_playua():
    soup = fetch_html(PLAY_UA)
    articles = soup.select(".short-article")
    articles_list = [parse_one_article_playua(article) for article in articles]
    articles_to_send = ""
    counter = 0
    for article in articles_list:
        counter += 1
        articles_to_send += f"<b>{counter}.</b> {article}.\n\n"
    articles_to_send += "<a href='https://playua.net/'><b>PlayUA website</b></a>"
    return articles_to_send


def parse_steam_sale_date():
    soup = fetch_html(STEAM_SALES)

    try:
        name = soup.select_one("a.text-green-400").text
        date = soup.select_one("p strong:nth-of-type(2)").text
        date_obj = datetime.strptime(date, "%m/%d/%Y")
        norm_date = date_obj.strftime("%d/%m/%Y")
        check_sale = soup.select_one("p.text-2xl").text

        if "is the next" in check_sale:
            return f"{name}\nDate of start: {norm_date}"
        else:
            return f"{name}\nDate of end: {norm_date}"
    except AttributeError:
        return "There are no information about steam sales right now!"


def parse_one_dou_activity(activity):
    def clean_text(text):
        return html.unescape(text.strip()).replace("\xa0", " ")

    name = clean_text(activity.select_one(".title").text)
    description = clean_text(activity.select_one(".b-typo").text)
    date = clean_text(activity.select_one(".date").text)
    price = clean_text(activity.select_one(".when-and-where span:nth-of-type(2)").text)

    return {
        "name": name,
        "description": description,
        "date": date,
        "price": price
    }


def parse_dou_for_activities():
    soup = fetch_html(DOU_LVIV_ACTIVITIES)
    activities = soup.select(".b-postcard")
    activities_list = [parse_one_dou_activity(activity) for activity in activities]
    activities_to_send = ""
    counter = 0
    for activity in activities_list:
        counter += 1
        activities_to_send += f"<b>{counter}.</b> <b>{activity['name']}</b>.\n<b>Date:</b> {activity['date']}\n{activity['description']}\n<b>Price:</b> {activity['price']}\n\n"
    activities_to_send += "<a href='https://dou.ua/calendar/city/Lviv/'><b>DOU website</b></a>"
    return activities_to_send
