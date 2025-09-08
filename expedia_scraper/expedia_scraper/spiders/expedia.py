# spiders/expedia.py
import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time
import random
import json

class ExpediaSpider(scrapy.Spider):
    name = "expedia"
    
    custom_settings = {
        'SELENIUM_DRIVER_ARGUMENTS': [
            '--headless=new',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--window-size=1920,1080',
            f'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '--disable-blink-features=AutomationControlled',
            '--disable-web-security',
            '--disable-extensions',
            '--disable-popup-blocking',
        ]
    }
    
    def start_requests(self):
        search_params = {
            'destination': 'Oaxaca, Oaxaca, Mexico',
            'startDate': '2025-09-09',
            'endDate': '2025-09-10',
            'adults': '1',
            'rooms': '1',
            'sort': 'RECOMMENDED'
        }
        
        url = f"https://www.expedia.com/Hotel-Search?{urlencode(search_params)}"
        
        yield SeleniumRequest(
            url=url,
            callback=self.parse,
            wait_time=30,
            wait_until=EC.presence_of_element_located((By.TAG_NAME, "body")),
            screenshot=True,
            script="Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
    
    def parse(self, response):
        driver = response.meta['driver']
        
        # Esperar y hacer scroll para cargar contenido
        time.sleep(random.uniform(5, 10))
        
        # Hacer scroll múltiple para cargar todos los hoteles
        for i in range(3):
            driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {i/3});")
            time.sleep(random.uniform(2, 4))
        
        # Verificar si hay bloqueo
        page_source = driver.page_source
        if "access denied" in page_source.lower() or "403" in page_source.lower():
            self.logger.error("BLOQUEO DETECTADO: 403 Forbidden")
            return
        
        # Usar el page source actualizado
        sel = scrapy.Selector(text=page_source)
        
        # Probar diferentes selectores
        selectors_to_try = [
            '[data-stid="property-card"]',
            '[data-test-id="property-card"]',
            '.uitk-card',
            '.listing-card',
            '[class*="hotel-card"]',
            '[class*="property-card"]'
        ]
        
        hotels = None
        for selector in selectors_to_try:
            hotels = sel.css(selector)
            if hotels:
                self.logger.info(f"Encontrados {len(hotels)} hoteles con selector: {selector}")
                break
        
        if not hotels:
            self.logger.error("No se encontraron hoteles. Selectores probados:")
            for selector in selectors_to_try:
                elements = sel.css(selector)
                self.logger.error(f"Selector '{selector}': {len(elements)} elementos")
            
            # Guardar página para debugging
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            self.logger.error("Página guardada en debug_page.html para análisis")
            return
        
        for hotel in hotels:
            yield {
                'name': self.extract_text(hotel, 'h3, [data-test-id="hotel-name"]'),
                'price': self.extract_text(hotel, '[data-test-id="price-summary"], .uitk-text'),
                'rating': self.extract_text(hotel, '[aria-label*="out of 10"], [data-test-id="review-score"]'),
                'reviews': self.extract_text(hotel, '[data-stid="review-count"], [data-test-id="review-count"]'),
                'location': self.extract_text(hotel, '[data-stid="hotel-address"], [data-test-id="location"]'),
                'url': response.urljoin(hotel.css('a::attr(href)').get())
            }
    
    def extract_text(self, element, selector):
        result = element.css(f'{selector}::text').get()
        if result:
            return ' '.join(result.strip().split())
        return None