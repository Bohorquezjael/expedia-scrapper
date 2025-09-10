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

def find_element_with_fallback(card, selectors):
    """Busca un elemento utilizando múltiples selectores como fallback"""
    for selector in selectors:
        try:
            element = card.find_element(By.CSS_SELECTOR, selector)
            if element.is_displayed() and element.text.strip():
                return element
        except (NoSuchElementException, Exception):
            continue
    return None

def extract_activity_data(card):
    activity_data = {}
    
    try:
        # Selectores para actividades (basados en investigación de Expedia)
        SELECTORS = {
            'name': [
                '[data-stid="activity-name"]',
                '[data-test-id="activity-name"]',
                'h3.activity-name',
                'h3.tour-name',
                'h3.uitk-heading',
                'h3[class*="title"]'
            ],
            'price': [
                '[data-stid="price-link"]',
                '[data-test-id="price-link"]',
                '.uitk-text.uitk-type-500.uitk-text-default-theme',
                '.price-value',
                '.activity-price',
                '[class*="price"]'
            ],
            'rating': [
                '[data-stid="rating"]',
                '[data-test-id="rating"]',
                '.uitk-badge-base-large span.is-visually-hidden',
                '.review-score',
                '[aria-label*="rating"]'
            ],
            'reviews': [
                '[data-stid="review-count"]',
                '[data-test-id="review-count"]',
                '.review-count',
                '.uitk-text.uitk-type-200',
                '[class*="review"]'
            ],
            'url': [
                '[data-stid="activity-link"]',
                '[data-test-id="activity-link"]',
                'a.activity-link',
                'a[href*="/activities/"]'
            ],
            'duration': [
                '[data-stid="duration"]',
                '[data-test-id="duration"]',
                '.duration-time',
                '[class*="duration"]'
            ],
            'category': [
                '[data-stid="activity-category"]',
                '[data-test-id="activity-category"]',
                '.activity-type',
                '[class*="category"]'
            ]
        }
        
        # Nombre
        name_element = find_element_with_fallback(card, SELECTORS['name'])
        activity_data['name'] = name_element.text.strip() if name_element else "Nombre no disponible"
        
        # Precio
        price_element = find_element_with_fallback(card, SELECTORS['price'])
        activity_data['price'] = price_element.text.strip() if price_element else "Precio no disponible"
        
        # Rating
        rating_element = find_element_with_fallback(card, SELECTORS['rating'])
        activity_data['rating'] = rating_element.text.strip() if rating_element else "Rating no disponible"
        
        # Reviews
        reviews_element = find_element_with_fallback(card, SELECTORS['reviews'])
        activity_data['reviews'] = reviews_element.text.strip() if reviews_element else "Reviews no disponibles"
        
        # URL
        try:
            url_element = find_element_with_fallback(card, SELECTORS['url'])
            if url_element:
                href = url_element.get_attribute("href") or ""
                activity_data['url'] = f"https://www.expedia.com{href}" if href and not href.startswith('http') else href
            else:
                activity_data['url'] = "URL no disponible"
        except:
            activity_data['url'] = "URL no disponible"
        
        # Duración (específico para actividades)
        duration_element = find_element_with_fallback(card, SELECTORS['duration'])
        activity_data['duration'] = duration_element.text.strip() if duration_element else "Duración no disponible"
        
        # Categoría (específico para actividades)
        category_element = find_element_with_fallback(card, SELECTORS['category'])
        activity_data['category'] = category_element.text.strip() if category_element else "Categoría no disponible"
            
    except Exception as e:
        print(f"Error extrayendo datos de actividad: {e}")
    
    return activity_data

def scrape_expedia_activities():
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
        # URL para actividades en Oaxaca
        url = "https://www.expedia.com/things-to-do/search?location=Oaxaca%2C%20Oaxaca%2C%20Mexico&startDate=2025-09-09&endDate=2025-09-10"
        
        print("🌐 Navegando a Expedia Activities...")
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
        
        print("🔍 Buscando actividades...")
        
        print("📜 Haciendo scroll...")
        for i in range(5):  # Más scroll para actividades (suelen tener más carga dinámica)
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script(f"window.scrollTo(0, {scroll_height * (i+1)/5})")
            time.sleep(2)
            close_popups(driver)
        
        print("⏳ Esperando a que carguen las actividades...")
        
        # Selectores específicos para actividades
        activity_selectors = [
            '[data-stid="activity-card"]',
            '[data-test-id="activity-card"]',
            '[data-stid="tour-card"]',
            '[data-test-id="tour-card"]',
            'div[data-stid="activity-listing"]',
            'div.activity-card',
            'div.tour-card',
            'div.attraction-card',
            'div[class*="activity-item"]'
        ]
        
        activities = None
        for selector in activity_selectors:
            try:
                activities = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
                if activities:
                    print(f"✅ Encontradas {len(activities)} actividades con: {selector}")
                    break
            except TimeoutException:
                print(f"⏭️  No se encontraron con: {selector}")
                continue
        
        if not activities:
            print("❌ NO SE PUDIERON ENCONTRAR ACTIVIDADES")
            driver.save_screenshot('debug_activities_screenshot.png')
            print("📸 Captura de pantalla guardada como 'debug_activities_screenshot.png'")
            
            with open('debug_activities_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("📄 HTML guardado como 'debug_activities_page.html'")
            return
        
        results = []
        print(f"📊 Procesando {len(activities)} actividades...")
        
        for i, activity in enumerate(activities):
            try:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", activity)
                time.sleep(0.5)  # Un poco más de tiempo para actividades
                
                activity_data = extract_activity_data(activity)
                results.append(activity_data)
                print(f"🎯 Actividad {i+1}: {activity_data['name']} - {activity_data['price']}")
                
            except Exception as e:
                print(f"❌ Error procesando actividad {i+1}: {e}")
                continue
        
        with open('actividades_oaxaca.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"💾 Guardadas {len(results)} actividades en 'actividades_oaxaca.json'")
        
        print("\n📋 RESUMEN:")
        for i, activity in enumerate(results[:5]):
            print(f"{i+1}. {activity['name']} - {activity['price']} - {activity['category']}")
        
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
    scrape_expedia_activities()