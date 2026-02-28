import os
import requests
import uuid
from dotenv import load_dotenv

load_dotenv()

AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY")
AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"


def get_token():
    """
    Получаем Access Token от GigaChat
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {AUTH_KEY}",
        "RqUID": str(uuid.uuid4())  # любой уникальный UUID
    }

    data = {
        "scope": "GIGACHAT_API_PERS"
    }

    r = requests.post(AUTH_URL, headers=headers, data=data, verify=False)
    print("TOKEN RESPONSE:", r.text)  # для диагностики
    r.raise_for_status()
    return r.json()["access_token"]


def ask_gigachat(prompt: str) -> str:
    """
    Отправляем запрос к GigaChat и возвращаем ответ
    """
    token = get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    r = requests.post(CHAT_URL, headers=headers, json=payload, verify=False)
    r.raise_for_status()

    return r.json()["choices"][0]["message"]["content"]
