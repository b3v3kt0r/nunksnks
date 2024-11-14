import re

def is_cyrillic_only(message_text):
    return bool(re.search(r"[а-яА-ЯёЁ]+", message_text))
