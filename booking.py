# booking_scraper_completo.py - VERSIÓN MEJORADA CON EXTRACCIÓN DE REVIEWS
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
            
            # Reviews count - MEJORADO
            try:
                reviews_text = review_container.text
                review_match = re.search(r'([\d\.,]+)\s*comentarios', reviews_text)
                if review_match:
                    hotel_data['review_count'] = review_match.group(1).replace('.', '').replace(',', '')
                    hotel_data['reviews'] = f"{review_match.group(1)} comentarios"
                else:
                    # Intentar método alternativo
                    try:
                        review_elements = review_container.find_elements(By.CSS_SELECTOR, 'div')
                        for element in review_elements:
                            text = element.text.strip()
                            if "comentario" in text.lower():
                                match = re.search(r'([\d\.,]+)\s*comentarios', text)
                                if match:
                                    hotel_data['review_count'] = match.group(1).replace('.', '').replace(',', '')
                                    hotel_data['reviews'] = f"{match.group(1)} comentarios"
                                    break
                        else:
                            hotel_data['review_count'] = "No disponible"
                            hotel_data['reviews'] = "No disponible"
                    except:
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

def handle_booking_popups(driver):
    """Maneja popups de Booking.com"""
    popup_selectors = [
        'button[aria-label*="Dismiss"]',
        'button[aria-label*="Close"]',
        'div[data-testid="modal-container"] button',
        'button:contains("×")',
        'button:contains("X")',
        'button[aria-label*="Cerrar"]',
        'button:contains("Aceptar")',
        'button:contains("Accept")'
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

def extract_hotel_reviews_sidebar(driver, hotel_url, max_reviews=10):
    """
    Extrae reseñas del sidebar modal de Booking.com
    Basado en el botón 'Leer todos los comentarios' :cite[4]
    """
    reviews = []
    original_window = driver.current_window_handle
    
    try:
        print(f"📖 Navegando a: {hotel_url[:80]}...")
        
        # Abrir nueva pestaña para las reseñas
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(hotel_url)
        
        # Esperar a que cargue la página
        time.sleep(4)
        handle_booking_popups(driver)
        
        # Intentar abrir el sidebar de reviews
        try:
            # Buscar y hacer click en el botón "Leer todos los comentarios"
            all_reviews_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="fr-read-all-reviews"]'))
            )
            driver.execute_script("arguments[0].click();", all_reviews_button)
            print("✅ Botón 'Leer todos los comentarios' clickeado")
            time.sleep(3)
            
            # Esperar a que cargue el sidebar
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, 'reviewCardsSection'))
            )
            print("✅ Sidebar de reviews cargado")
            
            # Extraer reseñas del sidebar
            reviews = extract_reviews_from_sidebar(driver, max_reviews)
            
            # Cerrar el sidebar
            try:
                close_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="Cerrar"], button[aria-label*="Close"]')
                driver.execute_script("arguments[0].click();", close_button)
                time.sleep(1)
            except:
                print("⚠️ No se pudo cerrar el sidebar automáticamente")
                
        except Exception as e:
            print(f"❌ No se pudo acceder a las reviews: {e}")
            # Método alternativo si el sidebar falla
            try:
                reviews = extract_reviews_alternative_method(driver, max_reviews)
            except Exception as alt_e:
                print(f"❌ Método alternativo también falló: {alt_e}")
        
    except Exception as e:
        print(f"❌ Error general extrayendo reseñas: {e}")
    finally:
        # Cerrar pestaña y volver a la principal
        driver.close()
        driver.switch_to.window(original_window)
    
    return reviews

def extract_reviews_from_sidebar(driver, max_reviews):
    """Extrae reviews del sidebar modal con scroll infinito :cite[2]"""
    reviews = []
    
    try:
        # Localizar el contenedor del sidebar
        sidebar = driver.find_element(By.ID, 'reviewCardsSection')
        
        print("🔄 Extrayendo reseñas con scroll...")
        
        # Hacer scroll para cargar más reviews
        last_height = driver.execute_script("return arguments[0].scrollHeight", sidebar)
        same_height_count = 0
        
        for attempt in range(5):
            # Scroll dentro del sidebar
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sidebar)
            time.sleep(2)
            
            # Verificar si hay nuevas reviews
            new_height = driver.execute_script("return arguments[0].scrollHeight", sidebar)
            if new_height == last_height:
                same_height_count += 1
                if same_height_count >= 2:
                    break
            else:
                same_height_count = 0
                last_height = new_height
        
        # Extraer todas las reviews visibles
        review_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="review-card"]')[:max_reviews]
        print(f"📝 Encontradas {len(review_elements)} reseñas")
        
        for i, review_element in enumerate(review_elements):
            try:
                review_data = extract_single_review_data(review_element)
                reviews.append(review_data)
                
                if (i + 1) % 5 == 0:
                    print(f"📦 Procesadas {i + 1} reseñas...")
                    
            except Exception as e:
                print(f"❌ Error extrayendo review {i + 1}: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Error en extracción de reviews: {e}")
    
    return reviews

def extract_single_review_data(review_element):
    """Extrae datos de una sola reseña :cite[1]:cite[6]"""
    review_data = {}
    
    try:
        # Rating de la reseña
        try:
            rating_element = review_element.find_element(By.CSS_SELECTOR, '[data-testid="review-score"]')
            review_data['rating'] = rating_element.text.strip()
        except:
            review_data['rating'] = "No disponible"
        
        # Título
        try:
            title_element = review_element.find_element(By.CSS_SELECTOR, '[data-testid="review-title"]')
            review_data['title'] = title_element.text.strip()
        except:
            review_data['title'] = "No disponible"
        
        # Contenido
        try:
            content_element = review_element.find_element(By.CSS_SELECTOR, '[data-testid="review-text"]')
            review_data['content'] = content_element.text.strip()
        except:
            review_data['content'] = "No disponible"
        
        # Autor y fecha
        try:
            meta_element = review_element.find_element(By.CSS_SELECTOR, '[data-testid="review-date"]')
            review_data['author_date'] = meta_element.text.strip()
        except:
            review_data['author_date'] = "No disponible"
        
        # Información adicional del reviewer
        try:
            info_element = review_element.find_element(By.CSS_SELECTOR, '[data-testid="reviewer-info"]')
            review_data['reviewer_info'] = info_element.text.strip()
        except:
            review_data['reviewer_info'] = "No disponible"
            
    except Exception as e:
        print(f"❌ Error extrayendo datos de review: {e}")
    
    return review_data

def extract_reviews_alternative_method(driver, max_reviews):
    """Método alternativo para extraer reviews si el sidebar falla"""
    reviews = []
    
    try:
        # Intentar encontrar reviews directamente en la página
        review_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="review-row"]')[:max_reviews]
        
        for review_element in review_elements:
            try:
                review_data = {}
                
                # Extraer datos básicos de la review
                try:
                    title_element = review_element.find_element(By.CSS_SELECTOR, '[data-testid="review-title"]')
                    review_data['title'] = title_element.text.strip()
                except:
                    review_data['title'] = "No disponible"
                
                try:
                    content_element = review_element.find_element(By.CSS_SELECTOR, '[data-testid="review-text"]')
                    review_data['content'] = content_element.text.strip()
                except:
                    review_data['content'] = "No disponible"
                
                reviews.append(review_data)
            except:
                continue
                
    except Exception as e:
        print(f"❌ Error en método alternativo: {e}")
    
    return reviews

def scrape_booking_complete(destination, checkin_date, checkout_date, max_hotels=50, max_reviews=10):
    """Función principal de scraping con extracción de reviews"""
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
                
                # Extraer reseñas si hay URL disponible
                hotel_url = hotel_data.get('url', '')
                if hotel_url and hotel_url != "URL no disponible":
                    print(f"📖 Extrayendo reseñas del hotel...")
                    hotel_data['reviews_detailed'] = extract_hotel_reviews_sidebar(driver, hotel_url, max_reviews)
                else:
                    hotel_data['reviews_detailed'] = []
                    print("⚠️ URL no disponible para extraer reseñas")
                
                all_hotels_data.append(hotel_data)
                
                print(f"✅ Hotel {i+1}: {hotel_data.get('name', 'Sin nombre')}")
                print(f"   ⭐ Rating: {hotel_data.get('rating', 'N/A')}")
                print(f"   📊 Reviews: {hotel_data.get('review_count', 'N/A')}")
                print(f"   📝 Reseñas extraídas: {len(hotel_data.get('reviews_detailed', []))}")
                
                # Pausa aleatoria entre hoteles
                sleep_time = random.uniform(2, 4)
                time.sleep(sleep_time)
                
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
            hotels_with_reviews = sum(1 for hotel in all_hotels_data if hotel.get('reviews_detailed'))
            
            print(f"📊 Reseñas totales extraídas: {total_reviews}")
            print(f"🏨 Hoteles con reseñas: {hotels_with_reviews}/{len(all_hotels_data)}")
        
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
    max_hotels = 30  # Reducido para pruebas
    max_reviews = 5   # Reducido para pruebas
    
    results = scrape_booking_complete(destination, checkin_date, checkout_date, max_hotels, max_reviews)
    
    if results:
        print(f"\n🎉 ¡Éxito! Extraídos {len(results)} hoteles")
        print(f"📝 Reseñas totales: {sum(len(h['reviews_detailed']) for h in results)}")
    else:
        print("\n❌ No se pudieron extraer datos")