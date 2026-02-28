import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")
URL = "https://api.deepseek.ai/v1/chat/completions"

def ask_deepseek(prompt):
    response = requests.post(
        URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "Ты эксперт по парфюмерии и ароматам."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
    )

    data = response.json()
    return data["choices"][0]["message"]["content"]
