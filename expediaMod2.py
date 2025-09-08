from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import random

def close_popups(driver):
    print("Buscando y cerrando popups...")
    
    popup_selectors = [
        'button[aria-label*="close"]',
        'button[aria-label*="dismiss"]',
        'button[class*="close"]',
        'button[class*="dismiss"]',
        'div[class*="overlay"] button',
        'div[class*="modal"] button',
        'div[class*="popup"] button',
        'svg[class*="close"]',
        'div[data-stid*="close"]',
        'button[data-stid*="close"]',
        'div[class*="backdrop"]',
    ]
    
    closed_count = 0
    for selector in popup_selectors:
        try:
            close_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            for button in close_buttons:
                try:
                    if button.is_displayed():
                        driver.execute_script("arguments[0].click();", button)
                        print(f"✅ Cerrado popup con selector: {selector}")
                        closed_count += 1
                        time.sleep(0.5)
                except:
                    continue
        except:
            continue
    
    try:
        from selenium.webdriver.common.keys import Keys
        body = driver.find_element(By.TAG_NAME, 'body')
        body.send_keys(Keys.ESCAPE)
        print("✅ Tecla Escape presionada")
        time.sleep(0.5)
    except:
        pass
    
    return closed_count

def extract_hotel_data(card):
    hotel_data = {}
    
    try:
        # URL
        try:
            href_element = card.find_element(By.CSS_SELECTOR, "[data-stid='open-hotel-information']")
            href = href_element.get_attribute("href") or ""
            hotel_data['url'] = f"https://www.expedia.com{href}" if not href.startswith('http') else href
        except:
            hotel_data['url'] = "URL no disponible"
        
        # Nombre
        try:
            name_element = card.find_element(By.CSS_SELECTOR, "h3.uitk-heading")
            hotel_data['name'] = name_element.text.strip()
        except:
            hotel_data['name'] = "Nombre no disponible"
        
        # Precio
        try:
            price_element = card.find_element(By.CSS_SELECTOR, ".uitk-text.uitk-type-end.uitk-type-300.uitk-text-default-theme")
            hotel_data['price'] = price_element.text.strip()
        except NoSuchElementException:
            try:
                price_elements = card.find_elements(By.CSS_SELECTOR, "[data-test-id='price-summary'] *")
                for elem in price_elements:
                    if "total" in elem.text.lower():
                        hotel_data['price'] = elem.text.strip()
                        break
                else:
                    hotel_data['price'] = "Precio no disponible"
            except:
                hotel_data['price'] = "Precio no disponible"
        except:
            hotel_data['price'] = "Precio no disponible"
        
        # Rating
        try:
            rating_element = card.find_element(By.CSS_SELECTOR, "span.uitk-badge-base-large span.is-visually-hidden")
            hotel_data['rating'] = rating_element.text.strip()
        except:
            hotel_data['rating'] = "Rating no disponible"
        
        # Reviews
        try:
            reviews_element = card.find_element(By.CSS_SELECTOR, "span.uitk-text.uitk-type-200")
            hotel_data['reviews'] = reviews_element.text.strip()
        except:
            hotel_data['reviews'] = "Reviews no disponibles"
            
    except Exception as e:
        print(f"Error extrayendo datos: {e}")
    
    return hotel_data

def scrape_expedia_manual():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        url = "https://www.expedia.com/Hotel-Search?destination=Oaxaca%2C%20Oaxaca%2C%20Mexico&startDate=2025-09-09&endDate=2025-09-10&adults=1&rooms=1&sort=RECOMMENDED"
        
        print("🌐 Navegando a Expedia...")
        driver.get(url)
        
        time.sleep(6)
        
        close_popups(driver)
        
        if "access denied" in driver.page_source.lower():
            print("❌ ¡BLOQUEO DETECTADO!")
            return
        
        time.sleep(4)
        close_popups(driver)
        
        print("🔍 Buscando hoteles...")
        
        print("📜 Haciendo scroll...")
        for i in range(3):
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script(f"window.scrollTo(0, {scroll_height * (i+1)/3})")
            time.sleep(2)
            close_popups(driver)
        
        print("⏳ Esperando a que carguen los hoteles...")
        
        main_selectors = [
            '[data-stid="property-card"]',
            '[data-test-id="property-card"]',
            'div[data-stid="lodging-card-responsive"]'
        ]
        
        hotels = None
        for selector in main_selectors:
            try:
                hotels = WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
                if hotels:
                    print(f"✅ Encontrados {len(hotels)} hoteles con: {selector}")
                    break
            except TimeoutException:
                print(f"⏭️  No se encontraron con: {selector}")
                continue
        
        if not hotels:
            print("⚠️  No se encontraron hoteles con selectores principales. Buscando alternativas...")
            
            alternative_selectors = [
                'div[class*="uitk-card"]',
                'section[data-stid*="property"]',
                'li[data-test-id*="property"]',
                'div[class*="listing"]'
            ]
            
            for selector in alternative_selectors:
                hotels = driver.find_elements(By.CSS_SELECTOR, selector)
                if hotels and len(hotels) > 2:
                    print(f"✅ Encontrados {len(hotels)} elementos con: {selector}")
                    break
        
        if not hotels:
            print("❌ NO SE PUDIERON ENCONTRAR HOTELES")
            driver.save_screenshot('error_screenshot.png')
            print("📸 Captura de pantalla guardada como 'error_screenshot.png'")
            return
        
        results = []
        print(f"📊 Procesando {len(hotels)} hoteles...")
        
        for i, hotel in enumerate(hotels):
            try:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", hotel)
                time.sleep(0.3)
                
                hotel_data = extract_hotel_data(hotel)
                
                results.append(hotel_data)
                print(f"🏨 Hotel {i+1}: {hotel_data['name']} - {hotel_data['price']}")
                
            except Exception as e:
                print(f"❌ Error procesando hotel {i+1}: {e}")
                continue
        
        with open('hoteles_oaxaca.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"💾 Guardados {len(results)} hoteles en 'hoteles_oaxaca.json'")
        
        print("\n📋 RESUMEN:")
        for i, hotel in enumerate(results[:3]):  # Mostrar primeros 3
            print(f"{i+1}. {hotel['name']} - {hotel['price']}")
        
        if len(results) > 3:
            print(f"... y {len(results) - 3} hoteles más")
        
        print("\n🔍 El navegador permanecerá abierto para inspección...")
        print("Presiona Enter en la terminal para cerrar")
        input()
        
    except Exception as e:
        print(f"❌ Error durante el scraping: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_expedia_manual()