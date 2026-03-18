import requests
import re
import urllib.parse
import logging
from typing import Optional
from base64 import b64encode

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PerfumeImageParser:
    def __init__(self, timeout: int = 12):
        self.timeout = timeout
        self.cache = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })
        logger.info("PerfumeImageParser инициализирован")

    def _request_text(self, url: str) -> str:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def search_fragrantica_page(self, brand: str, name: str) -> Optional[str]:
        queries = [
            f'{brand} {name} site:fragrantica.com perfume',
            f'{brand} {name} site:fragrantica.ru perfume',
            f'{brand} {name} fragrantica',
        ]

        patterns = [
            r'href="(https://www\.fragrantica\.com/perfume/[^"]+)"',
            r'href="(https://www\.fragrantica\.ru/perfume/[^"]+)"',
            r'<a[^>]+href="(https://www\.fragrantica\.[^"]+/perfume/[^"]+)"',
        ]

        for query in queries:
            search_url = f'https://www.bing.com/search?q={urllib.parse.quote(query)}'
            logger.info(f'Ищу страницу Fragrantica: {query}')

            try:
                html = self._request_text(search_url)
            except Exception as e:
                logger.error(f'Ошибка запроса к Bing: {e}')
                continue

            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for link in matches:
                    clean_link = link.replace('&amp;', '&')
                    if '/perfume/' in clean_link:
                        logger.info(f'Найдена страница Fragrantica: {clean_link}')
                        return clean_link

        return None

    def extract_image_from_fragrantica(self, page_url: str) -> Optional[str]:
        logger.info(f'Извлекаю изображение из Fragrantica: {page_url}')

        try:
            html = self._request_text(page_url)
        except Exception as e:
            logger.error(f'Ошибка загрузки страницы Fragrantica: {e}')
            return None

        patterns = [
            r'<meta property="og:image" content="([^"]+)"',
            r'<meta name="twitter:image" content="([^"]+)"',
            r'"image":"(https:[^"]+)"',
            r'src="(https://fimgs\.net/[^"]+\.(?:jpg|jpeg|png|webp))"',
            r'src="(https://[^"]+\.(?:jpg|jpeg|png|webp))"[^>]*class="[^"]*lazy[^"]*"',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                image_url = match.group(1).replace('\\/', '/')
                logger.info(f'Найдено изображение на Fragrantica: {image_url}')
                return image_url

        return None

    def search_image_direct(self, brand: str, name: str) -> Optional[str]:
        queries = [
            f'{brand} {name} perfume bottle',
            f'{brand} {name} fragrantica',
            f'{brand} {name} парфюм флакон',
        ]

        patterns = [
            r'"murl":"(https://[^"]+\.(?:jpg|jpeg|png|webp))"',
            r'"turl":"(https://[^"]+\.(?:jpg|jpeg|png|webp))"',
            r'src="(https://[^"]+\.(?:jpg|jpeg|png|webp))"',
            r'"mediaUrl":"(https://[^"]+\.(?:jpg|jpeg|png|webp))"',
        ]

        for query in queries:
            search_url = f'https://www.bing.com/images/search?q={urllib.parse.quote(query)}&form=HDRSC3'
            logger.info(f'Ищу прямую картинку: {query}')

            try:
                html = self._request_text(search_url)
            except Exception as e:
                logger.error(f'Ошибка поиска картинки в Bing Images: {e}')
                continue

            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for image_url in matches:
                    if any(bad in image_url.lower() for bad in ['logo', 'avatar', 'icon', 'sprite']):
                        continue
                    logger.info(f'Найдена прямая ссылка на картинку: {image_url}')
                    return image_url

        return None

    def validate_image_url(self, url: str) -> bool:
        if not url:
            return False
        if url.startswith('data:image/'):
            return True

        try:
            response = self.session.get(url, timeout=self.timeout, stream=True)
            content_type = response.headers.get('Content-Type', '').lower()
            is_valid = response.status_code == 200 and 'image' in content_type
            logger.info(f'Проверка картинки {url[:120]} -> {is_valid}')
            return is_valid
        except Exception as e:
            logger.error(f'Ошибка проверки картинки: {e}')
            return False

    def get_placeholder_url(self, brand: str, name: str) -> str:
        title = f"{brand} {name}".strip() or "Фото парфюма"
        safe_title = (
            title.replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;")
        )

        svg = f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="420" height="420" viewBox="0 0 420 420">
          <rect width="100%" height="100%" rx="28" fill="#f7f2ef"/>
          <rect x="110" y="70" width="200" height="240" rx="28" fill="#ead7d0" stroke="#784D61" stroke-width="4"/>
          <rect x="145" y="44" width="130" height="34" rx="10" fill="#784D61"/>
          <text x="210" y="338" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" fill="#784D61">{safe_title[:28]}</text>
          <text x="210" y="366" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#9a7d8d">изображение недоступно</text>
        </svg>
        """
        encoded = b64encode(svg.encode("utf-8")).decode("utf-8")
        return f"data:image/svg+xml;base64,{encoded}"

    def get_perfume_image(self, brand: str, name: str) -> str:
        if not brand or not name:
            return self.get_placeholder_url(brand or "Аромат", name or "")

        brand = brand.strip()
        name = name.strip()
        cache_key = f"{brand}_{name}".lower()

        if cache_key in self.cache:
            return self.cache[cache_key]

        image_url = None

        fragrantica_page = self.search_fragrantica_page(brand, name)
        if fragrantica_page:
            image_url = self.extract_image_from_fragrantica(fragrantica_page)
            if image_url and self.validate_image_url(image_url):
                self.cache[cache_key] = image_url
                return image_url

        image_url = self.search_image_direct(brand, name)
        if image_url and self.validate_image_url(image_url):
            self.cache[cache_key] = image_url
            return image_url

        placeholder = self.get_placeholder_url(brand, name)
        self.cache[cache_key] = placeholder
        return placeholder


_parser = None


def get_image_parser():
    global _parser
    if _parser is None:
        _parser = PerfumeImageParser()
    return _parser


def get_perfume_image(brand: str, name: str) -> str:
    parser = get_image_parser()
    return parser.get_perfume_image(brand, name)