# spiders/expedia_playwright.py
import scrapy
from scrapy_playwright.page import PageMethod
from urllib.parse import urlencode
import time

class ExpediaPlaywrightSpider(scrapy.Spider):
    name = "expedia_playwright"
    
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
        
        yield scrapy.Request(
            url=url,
            meta={
                'playwright': True,
                'playwright_page_methods': [
                    PageMethod('wait_for_selector', '[data-test-id="property-card"]', timeout=30000),
                    PageMethod('evaluate', 'window.scrollTo(0, document.body.scrollHeight)'),
                    PageMethod('wait_for_timeout', 3000),
                    PageMethod('evaluate', 'window.scrollTo(0, document.body.scrollHeight/2)'),
                    PageMethod('wait_for_timeout', 2000),
                ],
                'playwright_context_kwargs': {
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            },
            callback=self.parse
        )

    def parse(self, response):
        hotels = response.css('[data-test-id="property-card"]')
        
        if not hotels:
            self.logger.error("No se encontraron hoteles. Posible bloqueo.")
            # Guardar página para debugging
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            return
        
        self.logger.info(f"Encontrados {len(hotels)} hoteles")
        
        for hotel in hotels:
            yield {
                'name': self.clean_text(hotel.css('[data-test-id="hotel-name"]::text').get()),
                'price': self.clean_text(hotel.css('[data-test-id="price-summary"]::text').get()),
                'rating': self.clean_text(hotel.css('[data-test-id="review-score"]::text').get()),
                'reviews': self.clean_text(hotel.css('[data-test-id="review-count"]::text').get()),
                'location': self.clean_text(hotel.css('[data-test-id="location"]::text').get()),
                'url': response.urljoin(hotel.css('a::attr(href)').get())
            }
    
    def clean_text(self, text):
        return text.strip() if text else None