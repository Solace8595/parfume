import os
import uuid
import requests
import urllib3
from dotenv import load_dotenv

from image_parse import get_perfume_image
from llm.utils import get_shop_data, parse_model_response, normalize_perfume_item, fallback_item

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()


class GigaChatAPI:
    """
    Подключение к GigaChat для подбора парфюмерных ароматов
    """

    def __init__(self):
        self.auth_key = os.getenv("GIGACHAT_AUTH_KEY")
        if not self.auth_key:
            raise ValueError("GIGACHAT_AUTH_KEY не найден в .env файле")

        self.auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.chat_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        self.token = None

    def get_token(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self.auth_key}",
            "RqUID": str(uuid.uuid4())
        }

        data = {
            "scope": "GIGACHAT_API_PERS"
        }

        response = requests.post(
            self.auth_url,
            headers=headers,
            data=data,
            verify=False,
            timeout=60
        )

        if response.status_code == 200:
            self.token = response.json()["access_token"]
            return self.token

        raise ValueError(f"GigaChat auth error {response.status_code}: {response.text}")

    def get_perfume_recommendation(self, gender, aroma, season, shop_name, shop_link, associations=None):
        if not self.token:
            self.get_token()

        if shop_name == "Рив Гош":
            prompt = self._build_rivegauche_prompt(gender, aroma, season, shop_link, associations)
        else:
            prompt = self._build_general_prompt(gender, aroma, season, shop_name, shop_link, associations)

        return self._send_request(prompt)

    def _build_general_prompt(self, gender, aroma, season, shop_name, shop_link, associations=None):
        if not associations or associations.strip() == "":
            association_text = "утренней росой в цветущем саду"
        else:
            association_text = associations.strip()

        return f"""
Ты — профессиональный парфюмерный консультант с 10-летним опытом работы. Ты отлично знаешь ассортимент магазина {shop_name}, помнишь, какие ароматы есть в наличии, и можешь подобрать идеальный парфюм по самым тонким ассоциациям.

К тебе обратилась клиентка. Она просит подобрать {gender} {aroma} аромат для {season}. Ей нужен запах, напоминающий {association_text}.

Используя свои профессиональные знания и знание ассортимента {shop_name}, порекомендуй ровно 1 аромат, который идеально подходит под это описание и ЕСТЬ В НАЛИЧИИ в магазинах {shop_name} прямо сейчас.

ВАЖНЫЕ ТРЕБОВАНИЯ:
1. Аромат должен быть в наличии на сайте {shop_name} ({shop_link})
2. Укажи ссылку на КОНКРЕТНУЮ страницу товара на {shop_link}
3. Название и бренд укажи корректно
4. Цена должна соответствовать реальной цене на сайте для любого объёма, который есть в наличии
5. Для фото используй ссылку с {shop_link} или fragrantica.ru

Ответ представь ТОЛЬКО в формате JSON:

[
  {{
    "name": "название аромата",
    "brand": "бренд",
    "price": "цена в рублях",
    "link": "прямая ссылка на {shop_link}",
    "description": "описание 2-3 предложения, объясняющее, почему этот аромат подходит под ассоциацию",
    "image_url": "ссылка на фото флакона"
  }}
]

Не добавляй никакого текста до или после JSON. Верни только JSON.
"""

    def _build_rivegauche_prompt(self, gender, aroma, season, shop_link, associations=None):
        if not associations or associations.strip() == "":
            association_text = "утренней росой в цветущем саду — свежий, нежный, влажный, с зелёными нотами"
        else:
            association_text = associations.strip()

        return f"""
Ты — профессиональный парфюмерный консультант с 10-летним опытом работы в сети магазинов Рив Гош. Ты отлично знаешь ассортимент своего магазина, помнишь, какие ароматы есть в наличии, и можешь подобрать идеальный парфюм по самым тонким ассоциациям.

К тебе обратилась клиентка. Она просит подобрать {gender} {aroma} аромат для {season}. Ей нужен запах, напоминающий {association_text}.

Используя свои профессиональные знания и знание ассортимента Рив Гош, порекомендуй ровно 1 аромат, который идеально подходит под это описание и ЕСТЬ В НАЛИЧИИ в магазинах Рив Гош прямо сейчас.

ВАЖНЫЕ ТРЕБОВАНИЯ:
1. Аромат должен быть в наличии на сайте Рив Гош ({shop_link})
2. Укажи ссылку на КОНКРЕТНУЮ страницу товара на {shop_link}
3. Название и бренд укажи корректно
4. Цена должна соответствовать реальной цене на сайте для любого объёма, который есть в наличии
5. Для фото используй ссылку с {shop_link} или fragrantica.ru

Ответ представь ТОЛЬКО в формате JSON:

[
  {{
    "name": "название аромата",
    "brand": "бренд",
    "price": "цена в рублях",
    "link": "прямая ссылка на {shop_link}",
    "description": "описание 2-3 предложения, объясняющее, почему этот аромат подходит под ассоциацию",
    "image_url": "ссылка на фото флакона"
  }}
]

Не добавляй никакого текста до или после JSON. Верни только JSON.
"""

    def _send_request(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "GigaChat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 1000
        }

        response = requests.post(
            self.chat_url,
            headers=headers,
            json=payload,
            verify=False,
            timeout=60
        )

        if response.status_code == 401:
            self.token = None
            self.get_token()
            return self._send_request(prompt)

        if response.status_code != 200:
            raise ValueError(f"GigaChat API error {response.status_code}: {response.text}")

        result = response.json()
        return result["choices"][0]["message"]["content"]


def ask_gigachat(gender, aroma, season, associations, shop):
    client = GigaChatAPI()

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

    if item.get("brand") and item.get("name"):
        item["image_url"] = get_perfume_image(item["brand"], item["name"])
    else:
        item["image_url"] = get_perfume_image("Аромат", "Без названия")

    return item