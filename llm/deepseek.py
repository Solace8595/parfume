import json
import os
import requests
from dotenv import load_dotenv

from image_parse import get_perfume_image
from llm.utils import get_shop_data, parse_model_response, normalize_perfume_item, fallback_item

load_dotenv()


class DeepSeekOpenRouter:
    """
    Подключение к DeepSeek через OpenRouter для подбора парфюмерных ароматов
    """

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY не найден в .env файле")

        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://parfume-app.ru",
            "X-Title": "Perfume Finder App"
        }
        self.model = "deepseek/deepseek-chat"

    def get_perfume_recommendation(self, gender, aroma, season, shop_name, shop_link, associations=None):
        if not associations or associations.strip() == "":
            association_text = "утренней росой в цветущем саду"
        else:
            association_text = associations.strip()

        prompt = f"""
Порекомендуй ровно 1 {gender} парфюмерный аромат из {aroma} группы для {season}, который ассоциируется с {association_text}.

Пожалуйста, следуй этому алгоритму и покажи все шаги своих рассуждений:

ШАГ 1. Проанализируй ассоциацию "{association_text}". Какие ноты создают такое чувство? (влажная зелень, свежие цветы, прохлада)

ШАГ 2. Определи 2-3 конкретные парфюмерные ноты, которые соответствуют этим ощущениям.

ШАГ 3. Вспомни реальные ароматы, которые содержат эти ноты и относятся к {gender} {aroma}.

ШАГ 4. Выбери 1 аромат, который есть в наличии на сайте {shop_name} ({shop_link}). Проверь, что у него есть страница на сайте.

ШАГ 5. Только после всех рассуждений предоставь ответ в формате JSON.

ВАЖНЫЕ ТРЕБОВАНИЯ К JSON:
- Аромат должен быть в наличии на {shop_link}
- Ссылка должна вести на КОНКРЕТНУЮ страницу товара
- Цена должна соответствовать реальной цене на сайте для любого объёма в наличии
- Для фото используй ссылку с {shop_link} или fragrantica.ru

Формат JSON (только один объект в массиве):
[
  {{
    "name": "название",
    "brand": "бренд",
    "price": "цена в рублях",
    "link": "прямая ссылка на страницу с парфюмом на сайте",
    "description": "описание 2-3 предложения"
  }}
]

Верни только JSON без пояснений.
"""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Ты эксперт по парфюмерии. Отвечай подробно, следуя алгоритму."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 1500
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            raise ValueError(f"DeepSeek API error {response.status_code}: {response.text}")

        result = response.json()
        return result["choices"][0]["message"]["content"]


def ask_deepseek(gender, aroma, season, associations, shop):
    client = DeepSeekOpenRouter()

    shop_data = get_shop_data(shop)
    raw_response = client.get_perfume_recommendation(
        gender=gender,
        aroma=aroma,
        season=season,
        shop_name=shop_data["name"],
        shop_link=shop_data["url"],
        associations=associations
    )

    parsed = parse_model_response(raw_response)

    if parsed:
        item = normalize_perfume_item(parsed[0], raw_response)
    else:
        item = fallback_item(raw_response)

    if not item["image_url"] and item["brand"] and item["name"]:
        item["image_url"] = get_perfume_image(item["brand"], item["name"])

    return item