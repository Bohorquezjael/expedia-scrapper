from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json

def close_initial_modal(driver):
    print("🔍 Buscando modal inicial específico...")
    
    initial_modal_selectors = [
        'div[data-stid="form-modal"]',
        'div[data-test-id="signin-modal"]',
        'div[data-modal-id="signin"]',
        'div[role="dialog"][aria-label*="sign in"]',
        
        'div:contains("Continue with Google")',
        'div:contains("Continuar con Google")',
        'div:contains("Sign in")',
        'div:contains("Iniciar sesión")',
        
        'div[data-stid="subscription-modal"]',
        'div[data-test-id="email-signup-modal"]',
        
        'button[aria-label="Close"]',
        'button:contains("Maybe later")',
        'button:contains("No thanks")',
        'button:contains("Not now")',
        'button:contains("Cerrar")',
        'button:contains("Cancelar")',
        
        'div[data-stid="form-modal"] button',
        'div[data-test-id="signin-modal"] button',
        'div[role="dialog"] button'
    ]
    
    for selector in initial_modal_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                try:
                    if element.is_displayed():
                        print(f"✅ Encontrado modal inicial con: {selector}")
                        
                        if element.tag_name.lower() == 'button':
                            driver.execute_script("arguments[0].click();", element)
                            print(f"✅ Cerrado modal inicial con botón: {selector}")
                            return True
                        else:
                            close_buttons = element.find_elements(By.CSS_SELECTOR, 'button')
                            for btn in close_buttons:
                                if btn.is_displayed() and ('close' in btn.text.lower() or 'cancel' in btn.text.lower() or 'dismiss' in btn.text.lower()):
                                    driver.execute_script("arguments[0].click();", btn)
                                    print(f"✅ Cerrado modal inicial con botón interno: {btn.text}")
                                    return True
                except:
                    continue
        except:
            continue
    
    return False

def close_popups(driver):
    print("Buscando y cerrando popups...")
    
    if close_initial_modal(driver):
        time.sleep(2)
        return 1
    
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
        'button:contains("×")',
        'button:contains("X")',
        'button:contains("No thanks")',
        'button:contains("Maybe later")'
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
        closed_count += 1
        time.sleep(0.5)
    except:
        pass
    
    overlay_selectors = [
        'div[class*="overlay"]',
        'div[class*="backdrop"]',
        'div[class*="modal-backdrop"]'
    ]
    
    for selector in overlay_selectors:
        try:
            overlays = driver.find_elements(By.CSS_SELECTOR, selector)
            for overlay in overlays:
                if overlay.is_displayed():
                    try:
                        overlay.click()
                        print(f"✅ Cerrado overlay: {selector}")
                        closed_count += 1
                        time.sleep(0.5)
                    except:
                        driver.execute_script("arguments[0].style.display = 'none';", overlay)
                        print(f"✅ Overlay oculto con JS: {selector}")
                        closed_count += 1
        except:
            continue
    
    print(f"✅ Total de elementos cerrados: {closed_count}")
    return closed_count

def debug_modal(driver):
    print("🔍 Debuggeando modales presentes...")
    
    modal_indicators = [
        'div[role="dialog"]',
        'div[class*="modal"]',
        'div[class*="popup"]',
        'div[class*="overlay"]',
        'div[class*="backdrop"]',
        'div[data-stid]',
        'div[data-test-id]',
        'div[aria-modal="true"]'
    ]
    
    print("Elementos modales encontrados:")
    for selector in modal_indicators:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for i, element in enumerate(elements):
                if element.is_displayed():
                    print(f"📍 {selector}:")
                    print(f"   Texto: {element.text[:100]}...")
                    print(f"   Clases: {element.get_attribute('class')}")
                    print(f"   Data attributes: {element.get_attribute('data-stid') or element.get_attribute('data-test-id')}")
                    print("   ---")
        except:
            continue

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
        print("🔄 Página cargada, buscando modales...")
        
        debug_modal(driver)
        
        close_popups(driver)
        
        time.sleep(2)
        print("🔄 Verificando si quedan modales...")
        
        if "access denied" in driver.page_source.lower():
            print("❌ ¡BLOQUEO DETECTADO!")
            return
        
        time.sleep(3)
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
            print("❌ NO SE PUDIERON ENCONTRAR HOTELES")
            driver.save_screenshot('debug_screenshot.png')
            print("📸 Captura de pantalla guardada como 'debug_screenshot.png'")
            
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("📄 HTML guardado como 'debug_page.html'")
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
        for i, hotel in enumerate(results[:5]):
            print(f"{i+1}. {hotel['name']} - {hotel['price']}")
        
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