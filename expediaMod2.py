# expediaMod2.py - VERSIÓN CON CIERRE DE MODALES
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
import json
import random

def close_popups(driver):
    """Cierra todos los popups, modales y overlays posibles"""
    print("Buscando y cerrando popups...")
    
    # Selectores de elementos que podrían ser popups
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
            # Buscar elementos de cierre
            close_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            for button in close_buttons:
                try:
                    if button.is_displayed():
                        driver.execute_script("arguments[0].click();", button)
                        print(f"✅ Cerrado popup con selector: {selector}")
                        closed_count += 1
                        time.sleep(1)
                except:
                    continue
        except:
            continue
    
    # Intentar cerrar con Escape key (útil para modales)
    try:
        from selenium.webdriver.common.keys import Keys
        body = driver.find_element(By.TAG_NAME, 'body')
        body.send_keys(Keys.ESCAPE)
        print("✅ Tecla Escape presionada")
        time.sleep(1)
    except:
        pass
    
    return closed_count

def scrape_expedia_manual():
    # Configuración del navegador - NO headless
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        url = "https://www.expedia.com/Hotel-Search?destination=Oaxaca%2C%20Oaxaca%2C%20Mexico&startDate=2025-09-09&endDate=2025-09-10&adults=1&rooms=1&sort=RECOMMENDED"
        
        print("Navegando a Expedia...")
        driver.get(url)
        
        # Espera inicial
        time.sleep(5)
        
        # CERRAR POPUPS INMEDIATAMENTE
        close_popups(driver)
        
        # Verificar si hay bloqueo
        if "access denied" in driver.page_source.lower():
            print("¡BLOQUEO DETECTADO!")
            return
        
        # Esperar más y cerrar popups nuevamente
        time.sleep(3)
        close_popups(driver)
        
        print("Buscando hoteles...")
        
        # HACER SCROLL PARA CARGAR CONTENIDO
        print("Haciendo scroll para cargar contenido...")
        for i in range(3):
            scroll_position = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script(f"window.scrollTo(0, {scroll_position * (i+1)/3})")
            time.sleep(2)
            # Cerrar popups después de cada scroll
            close_popups(driver)
        
        # ESPERA INTELIGENTE para hoteles
        selectors_to_try = [
            '[data-test-id="property-card"]',
            '[data-stid="property-card"]',
            '[data-stid="lodging-card"]',
            'div[data-test-id="property-list"] div[class*="card"]',
            'li[data-test-id="property-list-item"]',
            'section[data-stid*="property"]',
            'div[class*="uitk-card"]',
            'div[class*="listing-card"]',
            'div[class*="hotel-card"]'
        ]
        
        hotels = None
        for selector in selectors_to_try:
            try:
                hotels = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
                if hotels:
                    print(f"✅ Encontrados {len(hotels)} hoteles con: {selector}")
                    break
            except TimeoutException:
                print(f"❌ No se encontraron con: {selector}")
                continue
        
        if not hotels:
            print("❌ No se encontraron hoteles. Probando selectores alternativos...")
            
            # Buscar cualquier elemento que parezca hotel
            alternative_selectors = [
                'div[class*="result"]',
                'div[class*="item"]',
                'div[class*="listing"]',
                'div[class*="property"]',
                'div[class*="hotel"]',
                'li[class*="result"]'
            ]
            
            for selector in alternative_selectors:
                hotels = driver.find_elements(By.CSS_SELECTOR, selector)
                if hotels and len(hotels) > 2:  # Si encuentra más de 2 elementos
                    print(f"✅ Encontrados {len(hotels)} elementos con: {selector}")
                    break
        
        if not hotels:
            print("❌ NO SE PUDIERON ENCONTRAR HOTELES")
            # Guardar página para análisis
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("Página guardada como 'debug_page.html'")
            
            # Mostrar vista actual del usuario
            driver.save_screenshot('current_view.png')
            print("Captura de pantalla guardada como 'current_view.png'")
            return
        
        # EXTRAER DATOS
        results = []
        print(f"Procesando {len(hotels)} hoteles...")
        
        for i, hotel in enumerate(hotels[:10]):  # Limitar a 10 para prueba
            try:
                # Asegurar que el elemento es visible
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", hotel)
                time.sleep(0.3)
                
                hotel_data = {}
                
                # Extraer nombre
                try:
                    name = hotel.find_element(By.CSS_SELECTOR, 'h3, h4, [data-test-id="hotel-name"], [class*="name"]')
                    hotel_data['name'] = name.text
                except:
                    hotel_data['name'] = "Nombre no disponible"
                
                # Extraer precio
                try:
                    price = hotel.find_element(By.CSS_SELECTOR, '[data-test-id="price-summary"], [class*="price"], [class*="amount"]')
                    hotel_data['price'] = price.text
                except:
                    hotel_data['price'] = "Precio no disponible"
                
                # Solo datos básicos para prueba
                results.append(hotel_data)
                print(f"Hotel {i+1}: {hotel_data['name']} - {hotel_data['price']}")
                
            except Exception as e:
                print(f"Error en hotel {i+1}: {e}")
                continue
        
        # GUARDAR RESULTADOS
        with open('hoteles_oaxaca.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Guardados {len(results)} hoteles")
        
        # Mantener abierto para inspección
        print("\n🔍 El navegador permanecerá abierto para inspección...")
        print("Presiona Enter en la terminal para cerrar")
        input()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        # Guardar error
        with open('error_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_expedia_manual()