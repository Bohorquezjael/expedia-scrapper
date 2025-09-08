# booking_stealth_scraper.py - VERSIÓN OPTIMIZADA PARA BOOKING.COM
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import json
import random
import requests
from bs4 import BeautifulSoup

def setup_stealth_driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-extensions")
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]
    
    options.add_argument(f"--user-agent={random.choice(user_agents)}")
    options.add_experimental_option("excludeSwitches", [
        "enable-automation",
        "enable-logging",
        "ignore-certificate-errors"
    ])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.images": 1,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.geolocation": 2
    })
    
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en', 'es'],
            });
            window.chrome = {
                runtime: {},
            };
        '''
    })
    
    return driver

def human_like_interactions(driver):
    print("🧠 Simulando comportamiento humano...")
    
    try:
        actions = ActionChains(driver)
        for _ in range(random.randint(2, 4)):
            x_offset = random.randint(-100, 100)
            y_offset = random.randint(-100, 100)
            actions.move_by_offset(x_offset, y_offset).perform()
            time.sleep(random.uniform(0.1, 0.3))
        scroll_parts = random.randint(3, 6)
        total_scroll = random.randint(800, 1500)
        
        for i in range(scroll_parts):
            scroll_amount = total_scroll // scroll_parts
            driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
            time.sleep(random.uniform(0.5, 1.2))
        body = driver.find_element(By.TAG_NAME, 'body')
        for _ in range(random.randint(1, 3)):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(random.uniform(0.4, 0.8))
        
        print("✅ Comportamiento humano simulado")
        
    except Exception as e:
        print(f"⚠️  Error en simulación humana: {e}")

def handle_booking_popups(driver):
    print("🛡️  Manejo de popups de Booking.com...")
    
    booking_popup_selectors = [
        'div[role="dialog"] button[aria-label*="Dismiss"]',
        'button[aria-label*="Close"]',
        'button[data-modal-aria-label-close]',
        'div[data-testid="modal-container"] button',
        'div[class*="modal-mask"] button',
        'div[class*="overlay"] button',
        'button[class*="close"]',
        'button[class*="dismiss"]',
        'div[data-capla-component="banner/prompt"] button',
        'div[class*="sign_in"] button',
        'div[class*="cookie"] button',
        'button:contains("Accept")',
        'button:contains("Reject")',
        'button:contains("×")',
        'button:contains("X")'
    ]
    
    closed_count = 0
    max_attempts = 2
    
    for attempt in range(max_attempts):
        for selector in booking_popup_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    try:
                        if element.is_displayed():
                            driver.execute_script("arguments[0].click();", element)
                            print(f"✅ Cerrado popup: {selector}")
                            closed_count += 1
                            time.sleep(random.uniform(0.3, 0.7))
                    except:
                        continue
            except:
                continue
        try:
            body = driver.find_element(By.TAG_NAME, 'body')
            body.send_keys(Keys.ESCAPE)
            print("✅ Tecla Escape presionada")
            time.sleep(0.5)
        except:
            pass
        
        time.sleep(1)
    
    return closed_count

def extract_hotel_data_booking(card):
    hotel_data = {}
    
    try:
        # Nombre del hotel
        try:
            name_element = card.find_element(By.CSS_SELECTOR, '[data-testid="title"]')
            hotel_data['name'] = name_element.text.strip()
        except:
            hotel_data['name'] = "Nombre no disponible"
        
        # Precio
        try:
            price_element = card.find_element(By.CSS_SELECTOR, '[data-testid="price-and-discounted-price"]')
            hotel_data['price'] = price_element.text.strip()
        except:
            try:
                price_element = card.find_element(By.CSS_SELECTOR, '.bui-price-display__value')
                hotel_data['price'] = price_element.text.strip()
            except:
                hotel_data['price'] = "Precio no disponible"
        
        # RATING Y REVIEWS
        try:
            review_container = card.find_element(By.CSS_SELECTOR, '[data-testid="review-score"]')
            try:
                rating_element = review_container.find_element(By.CSS_SELECTOR, 'div[aria-hidden="true"].f63b14ab7a')
                hotel_data['rating'] = rating_element.text.strip()
            except:
                hotel_data['rating'] = "Rating no disponible"
            try:
                evaluation_element = review_container.find_element(By.CSS_SELECTOR, '.f63b14ab7a.f54d35db44.bccbee2f63')
                hotel_data['evaluation'] = evaluation_element.text.strip()
            except:
                hotel_data['evaluation'] = "Evaluación no disponible"
            try:
                reviews_element = review_container.find_element(By.CSS_SELECTOR, '.fff1944c52.fb14de7f14.eaa8455879')
                hotel_data['reviews'] = reviews_element.text.strip()
                import re
                review_count = re.search(r'([\d\.]+)\s*comentarios', hotel_data['reviews'])
                if review_count:
                    hotel_data['review_count'] = review_count.group(1).replace('.', '')
                else:
                    hotel_data['review_count'] = "No disponible"
                    
            except:
                hotel_data['reviews'] = "Reviews no disponibles"
                hotel_data['review_count'] = "No disponible"
                
        except Exception as e:
            hotel_data['rating'] = "Rating no disponible"
            hotel_data['reviews'] = "Reviews no disponibles"
            hotel_data['review_count'] = "No disponible"
        
        # Ubicación
        try:
            location_element = card.find_element(By.CSS_SELECTOR, '[data-testid="address"]')
            hotel_data['location'] = location_element.text.strip()
        except:
            hotel_data['location'] = "Ubicación no disponible"
        
        # URL
        try:
            link_element = card.find_element(By.CSS_SELECTOR, 'a[data-testid="title-link"]')
            hotel_data['url'] = link_element.get_attribute('href')
        except:
            hotel_data['url'] = "URL no disponible"
        
        
            
    except Exception as e:
        print(f"❌ Error extrayendo datos: {e}")
    
    return hotel_data

def rapid_booking_extraction(driver):
    print("⚡ Extracción rápida de Booking.com...")
    
    results = []
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            hotel_selectors = [
                '[data-testid="property-card"]',
                'div[data-testid="property-card"]',
                'div[data-hotelid]',
                'div[class*="property-card"]',
                'div[class*="sr_property_block"]'
            ]
            
            hotels = []
            for selector in hotel_selectors:
                try:
                    hotels = driver.find_elements(By.CSS_SELECTOR, selector)
                    if hotels:
                        print(f"✅ Encontrados {len(hotels)} hoteles (intento {attempt + 1})")
                        break
                except:
                    continue
            
            if not hotels:
                print(f"❌ No se encontraron hoteles en intento {attempt + 1}")
                time.sleep(2)
                continue
            
            for i, hotel in enumerate(hotels[:15]): 
                try:
                    hotel_data = extract_hotel_data_booking(hotel)
                    results.append(hotel_data)
                    
                    if (i + 1) % 5 == 0:
                        print(f"📦 Extraídos {i + 1} hoteles...")
                        
                except Exception as e:
                    continue
            
            if results:
                break
                
        except Exception as e:
            print(f"❌ Error en intento {attempt + 1}: {e}")
            time.sleep(2)
    
    return results

def check_booking_detection(driver):
    
    try:
        detection_indicators = [
            'div[data-testid="no-search-results"]',
            'div:contains("No results found")',
            'div:contains("No se encontraron resultados")',
            'div:contains("access denied")',
            'div:contains("bot detected")',
            'div[class*="captcha"]',
            'iframe[src*="captcha"]',
            'div[class*="error"]'
        ]
        
        for selector in detection_indicators:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and any(el.is_displayed() for el in elements):
                    print("❌ Detección de bot identificada")
                    return True
            except:
                continue
        
        hotel_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="property-card"]')
        if len(hotel_elements) < 2:
            print("❌ Muy pocos resultados, posible detección")
            return True
            
        return False
        
    except:
        return False

def scrape_booking_stealth(destination, checkin_date, checkout_date):
    driver = setup_stealth_driver()
    
    try:
        base_url = "https://www.booking.com/searchresults.html"
        params = {
            'ss': destination,
            'checkin': checkin_date,
            'checkout': checkout_date,
            'group_adults': '1',
            'no_rooms': '1',
            'group_children': '0'
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        url = f"{base_url}?{query_string}"
        
        print(f"🌐 Navegando a Booking.com: {destination}")
        driver.get(url)
        
        initial_wait = random.uniform(5, 10)
        print(f"⏰ Espera inicial: {initial_wait:.1f}s")
        time.sleep(initial_wait)
        
        handle_booking_popups(driver)
        
        human_like_interactions(driver)
        
        if check_booking_detection(driver):
            print("🚨 Detección temprana! Ajustando estrategia...")
            time.sleep(3)
            handle_booking_popups(driver)
        
        print("⚡ Iniciando extracción rápida...")
        results = rapid_booking_extraction(driver)
        
        if check_booking_detection(driver):
            print("🚨 Detección durante extracción!")
            results = results[:1000]  
        
        if results:
            filename = "booking.json"
            # filename = f"booking_{destination.lower().replace(' ', '_')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Guardados {len(results)} hoteles en {filename}")
            
            print("\n📋 RESULTADOS OBTENIDOS:")
            for i, hotel in enumerate(results[:5]):
                print(f"{i+1}. {hotel.get('name', 'Sin nombre')} - {hotel.get('price', 'Sin precio')}")
            
            if len(results) > 5:
                print(f"... y {len(results) - 5} hoteles más")
        
        return results
        
    except Exception as e:
        print(f"❌ Error durante scraping: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        driver.quit()

def alternative_booking_approach():
    
    print("🔄 Intentando enfoque alternativo para Booking.com...")
    
    user_agent_configs = [
        {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "window-size": "1920,1080"
        },
        {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "window-size": "1440,900"
        },
        {
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "window-size": "1366,768"
        }
    ]
    
    for i, config in enumerate(user_agent_configs):
        print(f"🔧 Intentando configuración {i + 1}...")
        try:
            options = Options()
            for key, value in config.items():
                options.add_argument(f"--{key}={value}")
            
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            driver = webdriver.Chrome(options=options)
            driver.get("https://www.booking.com")
            
            time.sleep(4)
            human_like_interactions(driver)
            
            try:
                search_box = driver.find_element(By.CSS_SELECTOR, 'input[name="ss"]')
                search_box.send_keys("Oaxaca")
                search_box.send_keys(Keys.RETURN)
                time.sleep(5)
                
                results = rapid_booking_extraction(driver)
                if results:
                    print(f"✅ Éxito con configuración {i + 1}")
                    driver.quit()
                    return results
            except:
                continue
                
            driver.quit()
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ Error con configuración {i + 1}: {e}")
    
    return []

if __name__ == "__main__":
    print("🚀 Iniciando scraping de Booking.com con protección anti-detección...")
    
    destination = "Oaxaca, Mexico"
    checkin_date = "2025-09-09"
    checkout_date = "2025-09-10"
    
    results = scrape_booking_stealth(destination, checkin_date, checkout_date)
    
    if not results:
        print("🔄 Primer intento fallido, probando enfoque alternativo...")
        results = alternative_booking_approach()
    
    if results:
        print(f"\n🎉 ¡Éxito! Se extrajeron {len(results)} hoteles de Booking.com")
        print("💾 Los resultados han sido guardados en archivo JSON")
    else:
        print("\n❌ No se pudieron extraer datos de Booking.com.")
        print("💡 Recomendaciones para próximos intentos:")
        print("1. Usar proxies residenciales rotativos")
        print("2. Aumentar los tiempos de espera entre requests")
        print("3. Considerar usar la API oficial de Booking.com")
        print("4. Esperar 24-48 horas antes de reintentar")
    
    print("\n⚠️  Nota: El web scraping puede violar los Términos de Servicio.")
    print("   Asegúrate de cumplir con las regulaciones locales y los TOS del sitio.")
    
    input("\nPresiona Enter para salir...")