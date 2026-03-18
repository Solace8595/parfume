import json
import re


SHOP_MAPPING = {
    "ЛЭТУАЛЬ": {
        "name": "ЛЭТУАЛЬ",
        "url": "https://letu.ru"
    },
    "Золотое яблоко": {
        "name": "Золотое яблоко",
        "url": "https://goldapple.ru"
    },
    "Рив Гош": {
        "name": "Рив Гош",
        "url": "https://rivgosh.ru"
    }
}


def get_shop_data(shop_name: str) -> dict:
    return SHOP_MAPPING.get(shop_name, {
        "name": shop_name or "Золотое яблоко",
        "url": "https://goldapple.ru"
    })


def extract_json_from_text(text: str) -> str:
    """
    Пытается вытащить JSON из ответа модели.
    Поддерживает:
    - чистый JSON
    - ```json ... ```
    - текст до/после JSON
    - один объект вместо массива
    """
    if not text:
        return "[]"

    cleaned = text.strip()

    cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    if cleaned.startswith("[") and cleaned.endswith("]"):
        return cleaned

    if cleaned.startswith("{") and cleaned.endswith("}"):
        return f"[{cleaned}]"

    match_array = re.search(r"(\[\s*\{.*?\}\s*\])", cleaned, re.DOTALL)
    if match_array:
        return match_array.group(1)

    match_object = re.search(r"(\{\s*.*?\s*\})", cleaned, re.DOTALL)
    if match_object:
        return f"[{match_object.group(1)}]"

    return "[]"


def parse_model_response(text: str) -> list:
    json_text = extract_json_from_text(text)

    try:
        data = json.loads(json_text)
        if isinstance(data, dict):
            return [data]
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        return []

    return []


def normalize_perfume_item(item: dict, fallback_description: str = "") -> dict:
    return {
        "name": str(item.get("name", "")).strip(),
        "brand": str(item.get("brand", "")).strip(),
        "price": str(item.get("price", "")).strip(),
        "link": str(item.get("link", "")).strip(),
        "description": str(item.get("description", "")).strip() or fallback_description.strip(),
        "image_url": str(item.get("image_url", "")).strip()
    }


def fallback_item(raw_response: str = "") -> dict:
    return {
        "name": "",
        "brand": "",
        "price": "",
        "link": "",
        "description": raw_response.strip(),
        "image_url": ""
    }