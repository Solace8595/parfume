import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PERPLEXITY_API_KEY")
API_URL = "https://api.perplexity.ai/v1/answers"  # пример URL, нужно проверить у Perplexity

def ask_perplexity(prompt: str) -> str:
    """
    Отправляем запрос к Perplexity и возвращаем ответ
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": prompt,
        "limit": 1  # сколько ответов хотим
    }

    r = requests.post(API_URL, headers=headers, json=payload)
    r.raise_for_status()

    data = r.json()
    # здесь зависит от структуры ответа Perplexity
    # пример: data["answers"][0]["text"]
    return data.get("answers", [{}])[0].get("text", "Нет ответа")
