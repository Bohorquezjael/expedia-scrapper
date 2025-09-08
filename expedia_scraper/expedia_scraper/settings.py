# Scrapy settings for expedia_scraper project
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "expedia_scraper"

SPIDER_MODULES = ["expedia_scraper.spiders"]
NEWSPIDER_MODULE = "expedia_scraper.spiders"

# IMPORTANTE: Configuración para evitar bloqueos
ROBOTSTXT_OBEY = False  # Expedia suele tener restricciones estrictas en robots.txt:cite[2]

# Configuración de concurrencia y throttling
CONCURRENT_REQUESTS = 1  # Reducido para evitar bloqueos:cite[9]
CONCURRENT_REQUESTS_PER_DOMAIN = 1  # Muy conservador para Expedia:cite[9]
DOWNLOAD_DELAY = 8  # Delay aumentado significativamente:cite[9]
RANDOMIZE_DOWNLOAD_DELAY = True  # Aleatoriza el delay entre requests:cite[9]
AUTOTHROTTLE_ENABLED = True  # AutoThrottle para ajuste dinámico:cite[9]
AUTOTHROTTLE_START_DELAY = 10  # Delay inicial:cite[9]
AUTOTHROTTLE_MAX_DELAY = 90  # Delay máximo:cite[9]
AUTOTHROTTLE_TARGET_CONCURRENCY = 0.5  # Muy conservador para Expedia:cite[9]

# Configuración de reintentos
RETRY_ENABLED = True
RETRY_TIMES = 3  # Número de reintentos:cite[9]
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 403]  # Incluye 429:cite[5]
DOWNLOAD_TIMEOUT = 60  # Timeout aumentado:cite[9]

# User Agent y headers
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

# Cookies deshabilitadas (pueden ayudar a evitar detección)
COOKIES_ENABLED = False

# Configuración de Selenium
SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = None  # webdriver-manager lo manejará
SELENIUM_DRIVER_ARGUMENTS = [
    '--headless=new',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--window-size=1920,1080',
    '--disable-blink-features=AutomationControlled',
    '--disable-web-security',
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    '--disable-extensions',
    '--disable-popup-blocking',
]

# Middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
    'scrapy_selenium.SeleniumMiddleware': 800,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
}
# Pipelines (si los necesitas)
ITEM_PIPELINES = {
    # "expedia_scraper.pipelines.ExpediaScraperPipeline": 300,
}

# Configuración de logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'scrapy.log'
LOG_ENCODING = 'utf-8'

# Telnet Console (para debugging)
TELNETCONSOLE_ENABLED = True
TELNETCONSOLE_PORT = [6023, 6073]

# HTTP Cache (útil para desarrollo)
HTTPCACHE_ENABLED = False  # Desactivado en producción
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504, 403, 404, 408, 429]
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"