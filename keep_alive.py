from flask import Flask
import threading
import requests
import time
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def keep_alive():
    while True:
        try:
            requests.get("https://nunksnks.onrender.com")
            print("Keep-alive ping sent!")
        except Exception as e:
            print(f"Keep-alive error: {e}")
        time.sleep(60)


threading.Thread(target=keep_alive).start()

port = int(os.environ.get("PORT", 8000))
app.run(host="0.0.0.0", port=port)
