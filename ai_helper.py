from time import sleep
import os
from dotenv import load_dotenv

import cohere
from googleapiclient import discovery

load_dotenv()

COHERE_API_KEY=os.environ.get("COHERE_API_KEY")
PERSPECTIVE_API_KEY=os.environ.get("PERSPECTIVE_API_KEY")


def auto_replay_for_message(message_text):
    def generate_reply():
        co = cohere.ClientV2(COHERE_API_KEY)

        sleep(2)

        response = co.chat(
            model="command-r-plus",
            messages=[
                {
                    "role": "user",
                    "content": f"Give a response for this message like you're a personal assistant: {message_text}",
                }
            ]
        )

        return list(list(dict(response)["message"])[3][1][0])[1][1]


    reply = generate_reply()
    return reply 


def check_for_toxicity(message_text):
    client = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=PERSPECTIVE_API_KEY,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
        static_discovery=False,
    )

    analyze_request = {
        'comment': {'text': message_text},
        'requestedAttributes': {'TOXICITY': {}}
    }

    response = client.comments().analyze(body=analyze_request).execute()

    if response["attributeScores"]["TOXICITY"]["spanScores"][0]["score"]["value"] > 0.7:
        return True
    return False


def find_one_book():
    def generate_reply():
        co = cohere.ClientV2(COHERE_API_KEY)

        sleep(2)

        response = co.chat(
            model="command-r-plus",
            messages=[
                {
                    "role": "user",
                    "content": f"Write the name of one random book from ukrainian literature",
                }
            ]
        )

        return list(list(dict(response)["message"])[3][1][0])[1][1]


    reply = generate_reply()
    return reply 
