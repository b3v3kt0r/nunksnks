from flask import Flask
import threading
import requests
import time

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
        time.sleep(300)


threading.Thread(target=keep_alive).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
