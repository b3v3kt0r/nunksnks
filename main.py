import datetime
import threading
import os
from dotenv import load_dotenv

import telebot
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import ai_helper
from helpers import is_cyrillic_only
from keep_alive import run_flask
from parser import parse_news_playua, parse_steam_sale_date
from weather_checker import get_weather

load_dotenv()

bot = telebot.TeleBot(os.environ.get("TELEGRAM_API_KEY"))
uri = os.environ.get("MONGO_DB_URL")
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["bot_data"]



@bot.message_handler(commands=["start"])
def start_message(message):
    nickname = message.from_user.first_name or message.username or message.from_user.last_name

    markup = telebot.types.ReplyKeyboardMarkup()
    get_weather = telebot.types.KeyboardButton("Get the weather")
    get_articles = telebot.types.KeyboardButton("Get PlayUA top articles")
    get_steam_sale = telebot.types.KeyboardButton("Steam sale")
    markup.row(get_weather, get_articles, get_steam_sale)
    leave_note = telebot.types.KeyboardButton("Leave a note")
    get_notes = telebot.types.KeyboardButton("My notes")
    markup.row(leave_note, get_notes)
    markup.add(telebot.types.KeyboardButton("Who's creator of this godness?"))
    markup.add(telebot.types.KeyboardButton("Leave the feedback"))

    bot.reply_to(message, f"Hello, {nickname}! My name is Nunksnks.", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Who's creator of this godness?")
def answer_about_creator(message):
    bot.reply_to(message, "My creator's name is The Great Stanislav")


@bot.message_handler(func=lambda message: message.text == "Leave the feedback")
def feedback(message):
    markup = telebot.types.InlineKeyboardMarkup()
    bt1 = telebot.types.InlineKeyboardButton("I like it!", callback_data="Like")
    bt2 = telebot.types.InlineKeyboardButton("I'm bad peson!", callback_data="Dislike")
    markup.add(bt1, bt2)
    bot.reply_to(message, "You can leave only posistive feedback or we will find you!", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_feedback(call):
    nickname = call.from_user.first_name or call.from_user.username or call.from_user.last_name
    feedback = call.data
    user_id = call.from_user.id

    collection = db["feedbacks"]

    message_data = {
        "user": nickname,
        "opinion": feedback,
        "date_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    collection.update_one(
        {"user_id": user_id},
        {"$set": message_data},
        upsert=True
    )

    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    if feedback == "Like":
        # bot.answer_callback_query(call.id, "Bless you!")
        bot.send_message(call.message.chat.id, "Bless you!")
    elif feedback == "Dislike":
        # bot.answer_callback_query(call.id, "We will find you!")
        bot.send_message(call.message.chat.id, "We will find you!")


@bot.message_handler(func=lambda message: message.text == "Get the weather")
def weather(message):
        bot.reply_to(message, "Write name of the city")
        bot.register_next_step_handler(message, city_name)

def city_name(message):
    city = message.text
    weather = get_weather(city)
    bot.reply_to(message, weather)


# regexp=r"^(Who\'s creator of this godness\?|Leave the feedback|Get the weather|Leave a note)$"


@bot.message_handler(func=lambda message: message.text == "Leave a note")
def note(message):
    bot.reply_to(message, "Please, write it in the chat")
    bot.register_next_step_handler(message, save_note)

def save_note(message):
    nickname = message.from_user.first_name or message.username or message.from_user.last_name
    user_id = message.from_user.id

    collection = db["notes"]
    message_data = {
        "user": nickname,
        "user_id": user_id,
        "note": message.text,
        "date_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    collection.insert_one(message_data)

    bot.reply_to(message, "Nice one! You can check all your notes by writing \"My notes\" in the chat")


@bot.message_handler(func=lambda message: message.text == "Get PlayUA top articles")
def get_playua_articles(message):
    articles = parse_news_playua()
    articles_to_send = ""
    counter = 0
    for article in articles:
        counter += 1
        articles_to_send += f"{counter}. {article}\n"
    articles_to_send += "<a href='https://playua.net/'><b>PlayUA website</b></a>"
    bot.reply_to(message, articles_to_send, parse_mode="HTML")


@bot.message_handler(func=lambda message: message.text == "Steam sale")
def find_out_steam_sale(message):
    sale = parse_steam_sale_date()
    bot.reply_to(message, sale)


@bot.message_handler(func=lambda message: message.text == "My notes")
def get_all_notes(message):
    user_id = message.from_user.id

    collection = db["notes"]
    notes = list(collection.find({"user_id": user_id}))

    for note in notes:
        bot.send_message(message.chat.id, note["note"])


@bot.message_handler(content_types=["text"])
def info(message):

    nickname = message.from_user.first_name or message.username or message.from_user.last_name
    user_id = message.from_user.id

    collection = db[str(user_id)]
    message_data = {
        "user": nickname,
        "message": message.text,
        "date_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    collection.insert_one(message_data)

    message_text = message.text
    cheker = is_cyrillic_only(message_text)
    if cheker:
        bot.send_message(message.chat.id, "Sorry, I speak only english!")
        return

    toxicity = ai_helper.check_for_toxicity(message_text)
    if toxicity:
        bot.send_message(message.chat.id, "Fuck you!")
        return 

    response = ai_helper.auto_replay_for_message(message_text)
    bot.send_message(message.chat.id, response)
    # bot.send_message(message.chat.id, "Got it!")

def start_flask_thread():
    threading.Thread(target=run_flask, daemon=True).start()

def start_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    start_flask_thread()
    start_bot()
