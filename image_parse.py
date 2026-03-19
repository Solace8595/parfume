import re
import requests
import urllib.parse
import logging
from pathlib import Path
from base64 import b64encode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerfumeImageParser:
    def __init__(self, timeout: int = 12):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/127.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        })

        self.images_dir = Path("static/perfume_images")
        self.images_dir.mkdir(parents=True, exist_ok=True)

        logger.info("PerfumeImageParser инициализирован")

    def slug(self, brand, name):
        text = f"{brand}_{name}".lower()
        text = text.replace("ё", "е")
        text = re.sub(r"[^a-zа-я0-9]+", "_", text)
        return text.strip("_") or "perfume_image"

    def find_local(self, slug):
        for ext in ["jpg", "jpeg", "png", "webp"]:
            path = self.images_dir / f"{slug}.{ext}"
            if path.exists():
                logger.info(f"Используем сохранённую картинку: {path.name}")
                return f"/static/perfume_images/{path.name}"
        return None

    def _parse_bing_iusc_blocks(self, html):
        image_urls = []

        patterns = [
            r'class="iusc"[^>]*m="([^"]+)"',
            r"class='iusc'[^>]*m='([^']+)'",
            r'\bm="({&quot;.*?})"',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, flags=re.IGNORECASE | re.DOTALL)
            for raw in matches:
                try:
                    raw = raw.replace("&quot;", '"')
                    raw = raw.replace("\\/", "/")
                    import json
                    data = json.loads(raw)

                    for key in ["murl", "turl", "imgurl"]:
                        value = data.get(key)
                        if value and isinstance(value, str):
                            image_urls.append(value)
                except Exception:
                    continue

        return image_urls

    def _parse_bing_fallbacks(self, html):
        urls = []

        patterns = [
            r'"murl":"(.*?)"',
            r'"turl":"(.*?)"',
            r'"mediaUrl":"(.*?)"',
            r'"contentUrl":"(.*?)"',
            r'"thumbnailUrl":"(.*?)"',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, flags=re.IGNORECASE)
            for match in matches:
                urls.append(match.replace("\\/", "/").replace("&amp;", "&"))

        return urls

    def search_bing(self, brand, name):
        queries = [
            f"{brand} {name} perfume bottle",
            f"{brand} {name} fragrance bottle",
            f"{brand} {name}",
        ]

        for query in queries:
            logger.info(f"Поиск изображения: {query}")
            url = "https://www.bing.com/images/search?q=" + urllib.parse.quote(query)

            try:
                r = self.session.get(url, timeout=self.timeout)
                r.raise_for_status()
                html = r.text
            except Exception as e:
                logger.error(f"Ошибка запроса к Bing: {e}")
                continue

            candidates = []
            candidates.extend(self._parse_bing_iusc_blocks(html))
            candidates.extend(self._parse_bing_fallbacks(html))

            seen = set()
            filtered = []

            for image in candidates:
                image = image.strip()
                if not image or image in seen:
                    continue
                seen.add(image)

                if not image.startswith("http"):
                    continue

                if any(x in image.lower() for x in [
                    "logo", "sprite", "icon", "avatar", "favicon"
                ]):
                    continue

                filtered.append(image)

            if filtered:
                logger.info(f"Найдена ссылка: {filtered[0]}")
                return filtered[0]

        logger.warning("Картинка не найдена в Bing")
        return None

    def download(self, url, slug):
        try:
            r = self.session.get(url, stream=True, timeout=self.timeout)
            r.raise_for_status()

            content_type = r.headers.get("content-type", "").lower()

            if "image" not in content_type:
                logger.warning(f"Ссылка не является изображением: {url}")
                return None

            ext = "jpg"
            if "png" in content_type:
                ext = "png"
            elif "webp" in content_type:
                ext = "webp"
            elif "jpeg" in content_type:
                ext = "jpg"

            filename = f"{slug}.{ext}"
            path = self.images_dir / filename

            with open(path, "wb") as f:
                for chunk in r.iter_content(8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Картинка сохранена: {filename}")
            return f"/static/perfume_images/{filename}"

        except Exception as e:
            logger.error(f"Ошибка скачивания изображения: {e}")
            return None

    def placeholder(self, brand, name):
        text = f"{brand} {name}".strip()[:30] or "Фото парфюма"
        safe_text = (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
        )

        svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="420" height="420" viewBox="0 0 420 420">
  <rect width="100%" height="100%" rx="28" fill="#f7f2ef"/>
  <rect x="110" y="70" width="200" height="240" rx="28" fill="#ead7d0" stroke="#784D61" stroke-width="4"/>
  <rect x="145" y="44" width="130" height="34" rx="10" fill="#784D61"/>
  <text x="210" y="338" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" fill="#784D61">{safe_text}</text>
  <text x="210" y="366" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#9a7d8d">изображение недоступно</text>
</svg>
"""
        encoded = b64encode(svg.encode("utf-8")).decode("utf-8")
        return f"data:image/svg+xml;base64,{encoded}"

    def get_perfume_image(self, brand, name):
        if not brand or not name:
            return self.placeholder(brand or "Аромат", name or "")

        slug = self.slug(brand, name)

        local = self.find_local(slug)
        if local:
            return local

        image = self.search_bing(brand, name)
        if image:
            saved = self.download(image, slug)
            if saved:
                return saved

        logger.warning("Не удалось получить изображение, используется заглушка")
        return self.placeholder(brand, name)


_parser = None


def get_image_parser():
    global _parser
    if _parser is None:
        _parser = PerfumeImageParser()
    return _parser


def get_perfume_image(brand, name):
    parser = get_image_parser()
    return parser.get_perfume_image(brand, name)


def delete_saved_image(image_url: str):
    if not image_url:
        return

    prefix = "/static/perfume_images/"
    if not image_url.startswith(prefix):
        return

    filename = image_url.replace(prefix, "", 1)
    file_path = Path("static/perfume_images") / filename

    try:
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            logger.info(f"Удалено изображение: {filename}")
    except Exception as e:
        logger.error(f"Ошибка удаления изображения {filename}: {e}")