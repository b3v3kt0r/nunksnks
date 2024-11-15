import datetime
import threading
import telebot
import os
from dotenv import load_dotenv

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import ai_helper
from helpers import is_cyrillic_only
from keep_alive import run_flask
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
    markup.add(telebot.types.KeyboardButton("Who's creator of this godness?"))
    markup.add(telebot.types.KeyboardButton("Leave the feedback"))
    markup.add(telebot.types.KeyboardButton("Get the weather"))

    bot.reply_to(message, f"Hello, {nickname}! My name is Nunksnks.", reply_markup=markup)
    # bot.register_next_step_handler(message, on_click)


@bot.message_handler()
def buttons(message):
    if message.text == "Who's creator of this godness?":
        bot.reply_to(message, "My creator's name is The Great Stanislav")
    elif message.text == "Leave the feedback":
        markup = telebot.types.InlineKeyboardMarkup()
        bt1 = telebot.types.InlineKeyboardButton("I like it!", callback_data="Like")
        bt2 = telebot.types.InlineKeyboardButton("I'm bad peson!", callback_data="Dislike")
        markup.add(bt1, bt2)
        bot.reply_to(message, "You can leave only posistive feedback or we will find you!", reply_markup=markup)
    elif message.text == "Get the weather":
        bot.reply_to(message, "Write name of the city")
        bot.register_next_step_handler(message, city_name)


def city_name(message):
    city = message.text
    weather = get_weather(city)
    bot.reply_to(message, weather)
        

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

    # response = ai_helper.auto_replay_for_message(message_text)
    # bot.send_message(message.chat.id, response)
    bot.send_message(message.chat.id, "Got it!")

def start_flask_thread():
    threading.Thread(target=run_flask, daemon=True).start()

def start_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # start_flask_thread()
    start_bot()
