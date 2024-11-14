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

load_dotenv()

bot = telebot.TeleBot(os.environ.get("TELEGRAM_API_KEY"))
uri = os.environ.get("MONGO_DB_URL")
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["bot_data"]



@bot.message_handler(commands=["start"])
def start_message(message):
    nickname = message.from_user.first_name or message.username or message.from_user.last_name

    markup = telebot.types.ReplyKeyboardMarkup()
    btn1 = telebot.types.KeyboardButton("Write to creator")
    btn2 = telebot.types.KeyboardButton("Leave the feedback")
    markup.row(btn1)
    markup.row(btn2)

    bot.send_message(message.chat.id, f"Hello, {nickname}! My name is Nunksnks.", reply_markup=markup)
    bot.register_next_step_handler(message, on_click)


def on_click(message):
    if message.text == "Write to creator":
        bot.send_message(message.chat.id, "NO, you can't!")



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


def start_flask_thread():
    threading.Thread(target=run_flask, daemon=True).start()

def start_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    start_flask_thread()
    start_bot()
