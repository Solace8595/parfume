from image_parse import get_perfume_image
from llm.utils import get_shop_data


def ask_test(gender, aroma, season, associations, shop):
    shop_data = get_shop_data(shop)

    brand = "Chanel"
    name = "Chance Eau Tendre"
    association_text = associations.strip() if associations else "утренней росой в цветущем саду"

    image_url = get_perfume_image(brand, name)

    return {
        "name": name,
        "brand": brand,
        "price": "от 8 999 ₽",
        "link": shop_data["url"],
        "description": (
            f"Это тестовый результат для проверки итоговой страницы. "
            f"Аромат выбран как {gender} {aroma} вариант для {season}, "
            f"ассоциирующийся с образом: {association_text}."
        ),
        "image_url": image_url
    }