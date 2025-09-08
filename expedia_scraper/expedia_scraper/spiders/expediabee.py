# spiders/expedia_api.py
import scrapy
import json
from urllib.parse import urlencode
from scrapingbee import ScrapingBeeClient

class ExpediaApiSpider(scrapy.Spider):
    name = "expedia_api"
    
    def start_requests(self):
        # Tu API key de ScrapingBee (registro gratuito)
        API_KEY = 'EK0XY3V9C7ZGN8B9FAL61GCC6HI3J7BCBUEH3410CRWSKATGEQICE3LZKITMCBTHF081EHL72PZUPTC7'  # Regístrate en scrapingbee.com
        
        search_params = {
            'destination': 'Oaxaca, Oaxaca, Mexico',
            'startDate': '2025-09-09',
            'endDate': '2025-09-10',
            'adults': '1',
            'rooms': '1',
            'sort': 'RECOMMENDED'
        }
        
        url = f"https://www.expedia.com/Hotel-Search?{urlencode(search_params)}"
        
        client = ScrapingBeeClient(api_key=API_KEY)
        
        response = client.get(
            url,
            params={
                'wait': '3000',
                'block_resources': 'false',
                'premium_proxy': 'true',
                'country_code': 'us',
                'return_page_source': 'true'
            }
        )
        
        if response.status_code == 200:
            yield scrapy.http.HtmlResponse(
                url=url,
                body=response.content,
                encoding='utf-8'
            )
        else:
            self.logger.error(f"Error de ScrapingBee: {response.status_code}")

    def parse(self, response):
        # Selectores actualizados para Expedia 2024
        hotels = response.css('[data-test-id="property-card"]')
        
        self.logger.info(f"Encontrados {len(hotels)} hoteles")
        
        for hotel in hotels:
            yield {
                'name': hotel.css('[data-test-id="hotel-name"]::text').get(),
                'price': hotel.css('[data-test-id="price-summary"]::text').get(),
                'rating': hotel.css('[data-test-id="review-score"]::text').get(),
                'reviews': hotel.css('[data-test-id="review-count"]::text').get(),
                'location': hotel.css('[data-test-id="location"]::text').get(),
                'url': response.urljoin(hotel.css('a::attr(href)').get())
            }