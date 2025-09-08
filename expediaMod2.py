# expediaMod2.py - VERSIÓN STEALTH ANTI-DETECCIÓN
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def human_like_behavior(driver):
    """Simula comportamiento humano para evitar detección"""
    print("🧠 Simulando comportamiento humano...")
    
    try:
        # Movimientos de mouse aleatorios
        actions = ActionChains(driver)
        
        # Mover mouse en patrones aleatorios
        for _ in range(3):
            x = random.randint(100, 1000)
            y = random.randint(100, 800)
            actions.move_by_offset(x, y).perform()
            time.sleep(random.uniform(0.1, 0.5))
        
        # Scroll humano (no todo de una vez)
        scroll_parts = random.randint(3, 6)
        for i in range(scroll_parts):
            scroll_amount = random.randint(200, 500)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
            time.sleep(random.uniform(0.5, 1.5))
        
        # Teclas aleatorias
        body = driver.find_element(By.TAG_NAME, 'body')
        for _ in range(2):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(random.uniform(0.3, 0.8))
        
        print("✅ Comportamiento humano simulado")
        
    except Exception as e:
        print(f"❌ Error en simulación humana: {e}")

def stealth_driver():
    """Configuración stealth máxima para Chrome"""
    options = Options()
    
    # Configuración anti-detección
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
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-software-rasterizer")
    
    # Headers realistas
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Opciones experimentales para evitar detección
    options.add_experimental_option("excludeSwitches", [
        "enable-automation",
        "enable-logging",
        "ignore-certificate-errors",
        "test-type"
    ])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.images": 1,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    })
    
    driver = webdriver.Chrome(options=options)
    
    # Ejecutar scripts para ocultar WebDriver
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
                app: {
                    isInstalled: false,
                    InstallState: {
                        DISABLED: 'disabled',
                        INSTALLED: 'installed',
                        NOT_INSTALLED: 'not_installed'
                    },
                    RunningState: {
                        CANNOT_RUN: 'cannot_run',
                        READY_TO_RUN: 'ready_to_run',
                        RUNNING: 'running'
                    }
                }
            };
        '''
    })
    
    return driver

def check_if_results_vanished(driver):
    """Verifica si los resultados desaparecieron"""
    try:
        # Buscar indicadores de que los resultados se vaciaron
        empty_indicators = [
            'div[data-stid="property-listing-results"]:empty',
            'div[class*="no-results"]',
            'div[class*="empty"]',
            'div:contains("No results found")',
            'div:contains("No se encontraron resultados")'
        ]
        
        for selector in empty_indicators:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements and any(el.is_displayed() for el in elements):
                print("❌ Los resultados desaparecieron (detección anti-bot)")
                return True
        
        # Verificar si hay muy pocos elementos comparado con lo esperado
        hotel_elements = driver.find_elements(By.CSS_SELECTOR, '[data-stid="property-card"], [data-test-id="property-card"]')
        if len(hotel_elements) < 3:  # Si hay menos de 3 hoteles, probablemente se vació
            print("❌ Muy pocos resultados, probable detección")
            return True
            
        return False
        
    except:
        return False

def rapid_extraction(driver):
    """Extrae datos rápidamente antes de que Expedia detecte"""
    print("⚡ Extracción rápida antes de detección...")
    
    results = []
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            # Buscar hoteles inmediatamente
            hotel_selectors = [
                '[data-stid="property-card"]',
                '[data-test-id="property-card"]',
                'div[data-stid="lodging-card-responsive"]'
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
            
            # Extraer datos rápidamente
            for i, hotel in enumerate(hotels[:10]):  # Solo primeros 10 para velocidad
                try:
                    hotel_data = {}
                    
                    # Nombre (rápido)
                    try:
                        name = hotel.find_element(By.CSS_SELECTOR, "h3.uitk-heading")
                        hotel_data['name'] = name.text.strip()
                    except:
                        hotel_data['name'] = "Nombre no disponible"
                    
                    # Precio (rápido)
                    try:
                        price = hotel.find_element(By.CSS_SELECTOR, ".uitk-text.uitk-type-end.uitk-type-300.uitk-text-default-theme")
                        hotel_data['price'] = price.text.strip()
                    except:
                        hotel_data['price'] = "Precio no disponible"
                    
                    results.append(hotel_data)
                    
                    # Mostrar progreso cada 5 hoteles
                    if (i + 1) % 5 == 0:
                        print(f"📦 Extraídos {i + 1} hoteles...")
                        
                except Exception as e:
                    continue
            
            if results:
                break
                
        except Exception as e:
            print(f"❌ Error en intento {attempt + 1}: {e}")
            time.sleep(3)
    
    return results

def scrape_expedia_stealth():
    """Versión stealth con técnicas anti-detección"""
    driver = stealth_driver()
    
    try:
        # URL con parámetros simplificados
        url = "https://www.expedia.com/Hotel-Search?destination=Oaxaca&startDate=2025-09-09&endDate=2025-09-10&adults=1"
        
        print("🌐 Navegando a Expedia (modo stealth)...")
        driver.get(url)
        
        # Espera inicial aleatoria
        initial_wait = random.uniform(4, 8)
        print(f"⏰ Espera inicial: {initial_wait:.1f}s")
        time.sleep(initial_wait)
        
        # Comportamiento humano inmediato
        human_like_behavior(driver)
        
        # Verificar si ya nos detectaron
        if check_if_results_vanished(driver):
            print("🚨 Detectados! Reiniciando estrategia...")
            return []
        
        # Extracción RÁPIDA de datos
        print("⚡ Iniciando extracción rápida...")
        results = rapid_extraction(driver)
        
        # Verificar si desaparecieron los resultados durante la extracción
        if check_if_results_vanished(driver):
            print("🚨 Resultados desaparecieron durante extracción")
            # Intentar recuperar con scroll
            driver.execute_script("window.scrollTo(0, 0)")
            time.sleep(1)
            results = rapid_extraction(driver)
        
        if not results:
            print("❌ No se pudieron extraer datos")
            return []
        
        # Guardar resultados
        with open('hoteles_rapidos.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"💾 Guardados {len(results)} hoteles")
        
        # Mostrar resumen
        print("\n📋 RESULTADOS OBTENIDOS:")
        for i, hotel in enumerate(results[:5]):
            print(f"{i+1}. {hotel['name']} - {hotel['price']}")
        
        if len(results) > 5:
            print(f"... y {len(results) - 5} hoteles más")
        
        return results
        
    except Exception as e:
        print(f"❌ Error durante scraping stealth: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        driver.quit()

def alternative_approach():
    """Enfoque alternativo si el stealth falla"""
    print("🔄 Intentando enfoque alternativo...")
    
    # 1. Usar diferentes user agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    # 2. Intentar con diferentes ventanas
    for i, user_agent in enumerate(user_agents):
        print(f"🔧 Intentando con User Agent {i + 1}...")
        try:
            options = Options()
            options.add_argument(f"--user-agent={user_agent}")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            driver = webdriver.Chrome(options=options)
            driver.get("https://www.expedia.com/Hotel-Search?destination=Oaxaca")
            
            time.sleep(5)
            human_like_behavior(driver)
            
            results = rapid_extraction(driver)
            if results:
                print(f"✅ Éxito con User Agent {i + 1}")
                driver.quit()
                return results
                
            driver.quit()
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ Error con User Agent {i + 1}: {e}")
    
    return []

if __name__ == "__main__":
    print("🚀 Iniciando scraping con protección anti-detección...")
    
    # Primero intento: Modo stealth
    results = scrape_expedia_stealth()
    
    # Segundo intento: Enfoque alternativo si falla
    if not results:
        print("🔄 Primer intento fallido, probando enfoque alternativo...")
        results = alternative_approach()
    
    # Resultado final
    if results:
        print(f"\n🎉 ¡Éxito! Se extrajeron {len(results)} hoteles")
        print("💾 Resultados guardados en 'hoteles_rapidos.json'")
    else:
        print("\n❌ No se pudieron extraer datos. Expedia tiene fuertes protecciones.")
        print("💡 Recomendaciones:")
        print("1. Usar proxies rotativos")
        print("2. Esperar 24 horas antes de intentar nuevamente")
        print("3. Considerar usar una API de viajes en lugar de scraping")
    
    input("\nPresiona Enter para salir...")