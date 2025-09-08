# booking_scraper_completo.py - VERSIÓN MEJORADA
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
import re

def setup_stealth_driver():
    """Configura driver Chrome con técnicas stealth"""
    options = Options()
    
    # Configuración anti-detección
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    options.add_argument(f"--user-agent={random.choice(user_agents)}")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def human_like_scroll(driver, scroll_amount=3000):
    """Scroll humano para cargar más resultados"""
    print(f"📜 Haciendo scroll para cargar más hoteles...")
    
    total_scrolled = 0
    scroll_steps = random.randint(8, 15)
    
    for step in range(scroll_steps):
        scroll_increment = scroll_amount // scroll_steps
        driver.execute_script(f"window.scrollBy(0, {scroll_increment})")
        total_scrolled += scroll_increment
        
        # Comportamiento humano: pausas variables
        pause_time = random.uniform(0.5, 1.5)
        time.sleep(pause_time)
        
        # Cerrar popups durante el scroll
        if step % 3 == 0:
            handle_booking_popups(driver)
    
    print(f"✅ Scroll completado: {total_scrolled}px")
    return total_scrolled

def load_all_hotels(driver, max_hotels=100):
    """Carga todos los hoteles disponibles mediante scroll infinito"""
    print(f"🔄 Cargando hasta {max_hotels} hoteles...")
    
    hotels_loaded = 0
    previous_count = 0
    same_count_iterations = 0
    max_iterations = 10
    
    for iteration in range(max_iterations):
        # Obtener hoteles actuales
        current_hotels = driver.find_elements(By.CSS_SELECTOR, '[data-testid="property-card"]')
        current_count = len(current_hotels)
        
        print(f"📊 Iteración {iteration + 1}: {current_count} hoteles encontrados")
        
        # Verificar si alcanzamos el máximo
        if current_count >= max_hotels:
            print(f"🎉 ¡Meta alcanzada! {current_count} hoteles cargados")
            return current_hotels[:max_hotels]
        
        # Verificar si no hay más hoteles
        if current_count == previous_count:
            same_count_iterations += 1
            if same_count_iterations >= 2:
                print(f"⚠️  No hay más hoteles disponibles. Total: {current_count}")
                return current_hotels
        else:
            same_count_iterations = 0
        
        previous_count = current_count
        
        # Scroll para cargar más resultados
        human_like_scroll(driver, 2000)
        
        # Esperar a que carguen nuevos elementos
        time.sleep(random.uniform(2, 4))
    
    print(f"📦 Total final: {previous_count} hoteles")
    return driver.find_elements(By.CSS_SELECTOR, '[data-testid="property-card"]')[:max_hotels]

def extract_hotel_data_booking(card):
    """Extrae datos básicos del hotel"""
    hotel_data = {}
    
    try:
        # Nombre
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
            hotel_data['price'] = "Precio no disponible"
        
        # Rating y Reviews
        try:
            review_container = card.find_element(By.CSS_SELECTOR, '[data-testid="review-score"]')
            
            # Rating numérico
            try:
                rating_element = review_container.find_element(By.CSS_SELECTOR, 'div[aria-hidden="true"]')
                hotel_data['rating'] = rating_element.text.strip()
            except:
                hotel_data['rating'] = "No disponible"
            
            # Evaluación
            try:
                evaluation_elements = review_container.find_elements(By.CSS_SELECTOR, 'div')
                for elem in evaluation_elements:
                    text = elem.text.strip()
                    if text in ['Muy bien', 'Bien', 'Excelente', 'Fabuloso', 'Genial']:
                        hotel_data['evaluation'] = text
                        break
                else:
                    hotel_data['evaluation'] = "No disponible"
            except:
                hotel_data['evaluation'] = "No disponible"
            
            # Reviews count
            try:
                reviews_text = review_container.text
                review_match = re.search(r'([\d\.]+)\s*comentarios', reviews_text)
                if review_match:
                    hotel_data['review_count'] = review_match.group(1).replace('.', '')
                    hotel_data['reviews'] = f"{review_match.group(1)} comentarios"
                else:
                    hotel_data['review_count'] = "No disponible"
                    hotel_data['reviews'] = "No disponible"
            except:
                hotel_data['review_count'] = "No disponible"
                hotel_data['reviews'] = "No disponible"
                
        except:
            hotel_data['rating'] = "No disponible"
            hotel_data['evaluation'] = "No disponible"
            hotel_data['review_count'] = "No disponible"
            hotel_data['reviews'] = "No disponible"
        
        # URL
        try:
            link_element = card.find_element(By.CSS_SELECTOR, 'a[data-testid="title-link"]')
            hotel_data['url'] = link_element.get_attribute('href')
        except:
            hotel_data['url'] = "URL no disponible"
        
        # Ubicación
        try:
            location_element = card.find_element(By.CSS_SELECTOR, '[data-testid="address"]')
            hotel_data['location'] = location_element.text.strip()
        except:
            hotel_data['location'] = "Ubicación no disponible"
            
    except Exception as e:
        print(f"❌ Error extrayendo datos básicos: {e}")
    
    return hotel_data

def extract_hotel_reviews(driver, hotel_url, max_reviews=10):
    """Extrae reseñas detalladas de un hotel específico"""
    reviews = []
    
    try:
        print(f"📖 Extrayendo reseñas de: {hotel_url[:80]}...")
        
        # Abrir nueva pestaña para las reseñas
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(hotel_url)
        
        # Esperar a que cargue la página
        time.sleep(3)
        handle_booking_popups(driver)
        
        # Navegar a la sección de reseñas
        try:
            reviews_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href*="#tab-reviews"]'))
            )
            reviews_link.click()
            time.sleep(2)
        except:
            print("⚠️  No se pudo encontrar la sección de reseñas")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            return reviews
        
        # Extraer reseñas
        try:
            review_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="review-row"]')
            print(f"📝 Encontradas {len(review_elements)} reseñas")
            
            for i, review_element in enumerate(review_elements[:max_reviews]):
                try:
                    review_data = {}
                    
                    # Rating de la reseña
                    try:
                        review_rating = review_element.find_element(By.CSS_SELECTOR, '[data-testid="review-score"]')
                        review_data['rating'] = review_rating.text.strip()
                    except:
                        review_data['rating'] = "No disponible"
                    
                    # Título de la reseña
                    try:
                        review_title = review_element.find_element(By.CSS_SELECTOR, '[data-testid="review-title"]')
                        review_data['title'] = review_title.text.strip()
                    except:
                        review_data['title'] = "No disponible"
                    
                    # Contenido de la reseña
                    try:
                        review_content = review_element.find_element(By.CSS_SELECTOR, '[data-testid="review-text"]')
                        review_data['content'] = review_content.text.strip()
                    except:
                        review_data['content'] = "No disponible"
                    
                    # Autor y fecha
                    try:
                        review_meta = review_element.find_element(By.CSS_SELECTOR, '[data-testid="review-date"]')
                        review_data['author_date'] = review_meta.text.strip()
                    except:
                        review_data['author_date'] = "No disponible"
                    
                    reviews.append(review_data)
                    
                except Exception as e:
                    print(f"❌ Error extrayendo reseña {i+1}: {e}")
                    continue
                
        except Exception as e:
            print(f"❌ Error encontrando reseñas: {e}")
        
        # Cerrar pestaña y volver
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        
    except Exception as e:
        print(f"❌ Error general extrayendo reseñas: {e}")
        # Asegurarse de volver a la pestaña principal
        if len(driver.window_handles) > 1:
            driver.close()
        driver.switch_to.window(driver.window_handles[0])
    
    return reviews

def handle_booking_popups(driver):
    """Maneja popups de Booking.com"""
    popup_selectors = [
        'button[aria-label*="Dismiss"]',
        'button[aria-label*="Close"]',
        'div[data-testid="modal-container"] button',
        'button:contains("×")',
        'button:contains("X")'
    ]
    
    for selector in popup_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                if element.is_displayed():
                    driver.execute_script("arguments[0].click();", element)
                    time.sleep(0.5)
        except:
            continue

def scrape_booking_complete(destination, checkin_date, checkout_date, max_hotels=100, max_reviews=10):
    """Función principal de scraping"""
    driver = setup_stealth_driver()
    all_hotels_data = []
    
    try:
        # Construir URL
        base_url = "https://www.booking.com/searchresults.html"
        params = {
            'ss': destination,
            'checkin': checkin_date,
            'checkout': checkout_date,
            'group_adults': '2',
            'no_rooms': '1',
            'group_children': '0'
        }
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        url = f"{base_url}?{query_string}"
        
        print(f"🌐 Navegando a: {destination}")
        driver.get(url)
        
        # Esperar inicial
        time.sleep(5)
        handle_booking_popups(driver)
        
        # Cargar todos los hoteles
        all_hotels = load_all_hotels(driver, max_hotels)
        print(f"🏨 Total de hoteles a procesar: {len(all_hotels)}")
        
        # Extraer datos de cada hotel
        for i, hotel in enumerate(all_hotels):
            try:
                print(f"\n🔍 Procesando hotel {i+1}/{len(all_hotels)}")
                
                # Scroll para hacer visible
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", hotel)
                time.sleep(0.5)
                
                # Datos básicos
                hotel_data = extract_hotel_data_booking(hotel)
                
                # Extraer reseñas si hay URL
                if hotel_data.get('url') and hotel_data['url'] != "URL no disponible":
                    hotel_data['reviews_detailed'] = extract_hotel_reviews(driver, hotel_data['url'], max_reviews)
                else:
                    hotel_data['reviews_detailed'] = []
                
                all_hotels_data.append(hotel_data)
                
                print(f"✅ Hotel {i+1}: {hotel_data.get('name', 'Sin nombre')}")
                print(f"   📊 Reseñas extraídas: {len(hotel_data.get('reviews_detailed', []))}")
                
                # Pausa aleatoria entre hoteles
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"❌ Error procesando hotel {i+1}: {e}")
                continue
        
        # Guardar resultados
        if all_hotels_data:
            filename = f"booking_{destination.lower().replace(' ', '_')}_completo.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_hotels_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Guardados {len(all_hotels_data)} hoteles con reseñas en {filename}")
            
            # Estadísticas
            total_reviews = sum(len(hotel.get('reviews_detailed', [])) for hotel in all_hotels_data)
            print(f"📊 Reseñas totales extraídas: {total_reviews}")
        
        return all_hotels_data
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        driver.quit()

# USO
if __name__ == "__main__":
    print("🚀 Iniciando scraping completo de Booking.com...")
    
    # Configuración
    destination = "Oaxaca, Mexico"
    checkin_date = "2025-09-09"
    checkout_date = "2025-09-10"
    max_hotels = 100  # Máximo de hoteles a extraer
    max_reviews = 10  # Reseñas por hotel
    
    results = scrape_booking_complete(destination, checkin_date, checkout_date, max_hotels, max_reviews)
    
    if results:
        print(f"\n🎉 ¡Éxito! Extraídos {len(results)} hoteles")
        print(f"📝 Reseñas totales: {sum(len(h['reviews_detailed']) for h in results)}")
    else:
        print("\n❌ No se pudieron extraer datos")