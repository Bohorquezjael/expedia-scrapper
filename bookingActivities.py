from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import random
import re
from urllib.parse import quote

def setup_stealth_driver():
    options = Options()
    
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

def handle_booking_popups(driver):
    """Maneja popups y cookies en Booking.com"""
    popup_selectors = [
        'button[aria-label*="Dismiss"]',
        'button[aria-label*="Close"]',
        'button[aria-label*="Aceptar"]',
        'button[aria-label*="Accept"]',
        '#cookiebanner .button',
        '.cookie-popup .accept',
        'div[data-testid="modal-container"] button'
    ]
    
    for selector in popup_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                if element.is_displayed():
                    element.click()
                    print("✅ Popup cerrado")
                    time.sleep(1)
                    break
        except:
            continue

def human_like_scroll(driver, scroll_amount=3000):
    """Scroll suave y humano para cargar más contenido"""
    print(f"📜 Haciendo scroll para cargar más actividades...")
    
    total_scrolled = 0
    scroll_steps = random.randint(8, 15)
    
    for step in range(scroll_steps):
        scroll_increment = scroll_amount // scroll_steps
        driver.execute_script(f"window.scrollBy(0, {scroll_increment})")
        total_scrolled += scroll_increment
        
        pause_time = random.uniform(0.5, 1.5)
        time.sleep(pause_time)
        
        if step % 3 == 0:
            handle_booking_popups(driver)
    
    print(f"✅ Scroll completado: {total_scrolled}px")
    return total_scrolled

def load_all_activities(driver, max_activities=50):
    """Carga todas las actividades disponibles con scroll infinito"""
    print(f"🔄 Cargando hasta {max_activities} actividades...")
    
    previous_count = 0
    same_count_iterations = 0
    max_iterations = 8
    
    for iteration in range(max_iterations):
        # Selectores específicos para actividades basados en la estructura de Booking
        current_activities = driver.find_elements(By.CSS_SELECTOR, '[data-testid*="activity"], .activity-card, .thing-to-do-card, [class*="activity-item"], [class*="card"]')
        current_count = len(current_activities)
        
        print(f"📊 Iteración {iteration + 1}: {current_count} actividades encontradas")
        
        if current_count >= max_activities:
            print(f"🎉 ¡Meta alcanzada! {current_count} actividades cargadas")
            return current_activities[:max_activities]
        
        if current_count == previous_count:
            same_count_iterations += 1
            if same_count_iterations >= 2:
                print(f"⚠️  No hay más actividades disponibles. Total: {current_count}")
                return current_activities
        else:
            same_count_iterations = 0
        
        previous_count = current_count
        
        human_like_scroll(driver, 2000)
        time.sleep(random.uniform(2, 4))
    
    print(f"📦 Total final: {previous_count} actividades")
    return driver.find_elements(By.CSS_SELECTOR, '[data-testid*="activity"], .activity-card, .thing-to-do-card, [class*="activity-item"], [class*="card"]')[:max_activities]

def extract_activity_data(card):
    """Extrae datos de una tarjeta de actividad individual"""
    activity_data = {}
    
    try:
        # Nombre de la actividad
        try:
            name_element = card.find_element(By.CSS_SELECTOR, '[data-testid*="title"], [class*="title"], [class*="name"], h3, h4')
            activity_data['name'] = name_element.text.strip()
        except:
            activity_data['name'] = "Nombre no disponible"
        
        # Precio
        try:
            price_element = card.find_element(By.CSS_SELECTOR, '[data-testid*="price"], [class*="price"], [class*="amount"], [class*="cost"]')
            activity_data['price'] = price_element.text.strip()
        except:
            activity_data['price'] = "Precio no disponible"
        
        # Rating
        try:
            rating_element = card.find_element(By.CSS_SELECTOR, '[data-testid*="rating"], [class*="rating"], [class*="score"], [aria-label*="rating"]')
            activity_data['rating'] = rating_element.text.strip()
        except:
            activity_data['rating'] = "No disponible"
        
        # Número de reviews
        try:
            reviews_element = card.find_element(By.CSS_SELECTOR, '[data-testid*="review"], [class*="review"], [class*="comment"]')
            reviews_text = reviews_element.text.strip()
            review_match = re.search(r'(\d+)\s*(?:reviews|reseñas|comentarios|opiniones)', reviews_text, re.IGNORECASE)
            if review_match:
                activity_data['review_count'] = review_match.group(1)
                activity_data['reviews'] = f"{review_match.group(1)} reseñas"
            else:
                activity_data['review_count'] = "No disponible"
                activity_data['reviews'] = "No disponible"
        except:
            activity_data['review_count'] = "No disponible"
            activity_data['reviews'] = "No disponible"
        
        # Duración
        try:
            duration_element = card.find_element(By.CSS_SELECTOR, '[data-testid*="duration"], [class*="duration"], [class*="time"]')
            activity_data['duration'] = duration_element.text.strip()
        except:
            activity_data['duration'] = "Duración no disponible"
        
        # Categoría/Tipo
        try:
            category_element = card.find_element(By.CSS_SELECTOR, '[data-testid*="category"], [class*="category"], [class*="type"]')
            activity_data['category'] = category_element.text.strip()
        except:
            activity_data['category'] = "Categoría no disponible"
        
        # URL
        try:
            link_element = card.find_element(By.CSS_SELECTOR, 'a')
            activity_data['url'] = link_element.get_attribute('href')
        except:
            activity_data['url'] = "URL no disponible"
        
        # Proveedor/Operador
        try:
            provider_element = card.find_element(By.CSS_SELECTOR, '[data-testid*="provider"], [class*="provider"], [class*="operator"]')
            activity_data['provider'] = provider_element.text.strip()
        except:
            activity_data['provider'] = "Proveedor no disponible"
            
    except Exception as e:
        print(f"❌ Error extrayendo datos básicos: {e}")
    
    return activity_data

def scrape_booking_activities_oaxaca(max_activities=20):
    """Scraping específico para actividades en Oaxaca usando la URL funcional"""
    driver = setup_stealth_driver()
    all_activities_data = []
    
    try:
        # URL específica para actividades en Oaxaca (la que proporcionaste que funciona)
        url = "https://www.booking.com/attractions/searchresults/mx/oaxaca-de-juarez.es.html"
        
        print(f"🌐 Navegando a: {url}")
        driver.get(url)
        
        time.sleep(5)
        handle_booking_popups(driver)
        
        # Esperar a que carguen las actividades
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid*="activity"], .activity-card, .thing-to-do-card'))
            )
        except TimeoutException:
            print("⚠️  No se encontraron actividades con los selectores esperados. Intentando con selectores alternativos...")
        
        all_activities = load_all_activities(driver, max_activities)
        print(f"🎯 Total de actividades a procesar: {len(all_activities)}")
        
        for i, activity in enumerate(all_activities):
            try:
                print(f"\n🔍 Procesando actividad {i+1}/{len(all_activities)}")
                
                # Scroll para hacer visible la actividad
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", activity)
                time.sleep(0.5)
                
                activity_data = extract_activity_data(activity)
                all_activities_data.append(activity_data)
                
                print(f"✅ Actividad {i+1}: {activity_data.get('name', 'Sin nombre')}")
                print(f"   💰 Precio: {activity_data.get('price', 'N/A')}")
                print(f"   ⭐ Rating: {activity_data.get('rating', 'N/A')}")
                print(f"   📊 Reviews: {activity_data.get('review_count', 'N/A')}")
                
                # Espera aleatoria entre requests
                sleep_time = random.uniform(1, 3)
                time.sleep(sleep_time)
                
            except Exception as e:
                print(f"❌ Error procesando actividad {i+1}: {e}")
                continue
        
        # Guardar resultados
        if all_activities_data:
            filename = f"booking_activities_oaxaca_{time.strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_activities_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Guardadas {len(all_activities_data)} actividades en {filename}")
            
            # Mostrar resumen estadístico
            activities_with_price = sum(1 for a in all_activities_data if a.get('price') != "Precio no disponible")
            activities_with_rating = sum(1 for a in all_activities_data if a.get('rating') != "No disponible")
            activities_with_reviews = sum(1 for a in all_activities_data if a.get('review_count') != "No disponible")
            
            print(f"📊 ESTADÍSTICAS:")
            print(f"   💰 Actividades con precio: {activities_with_price}/{len(all_activities_data)}")
            print(f"   ⭐ Actividades con rating: {activities_with_rating}/{len(all_activities_data)}")
            print(f"   📝 Actividades con reviews: {activities_with_reviews}/{len(all_activities_data)}")
            
            # Mostrar algunas actividades de ejemplo
            print(f"\n🎯 ACTIVIDADES EN OAXACA ENCONTRADAS:")
            for j, activity in enumerate(all_activities_data[:5]):
                print(f"{j+1}. {activity.get('name', 'Sin nombre')}")
                print(f"   Precio: {activity.get('price', 'N/A')}")
                print(f"   Rating: {activity.get('rating', 'N/A')}")
                print(f"   Duración: {activity.get('duration', 'N/A')}")
                print()
        
        return all_activities_data
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        driver.quit()

def main():
    print("🚀 Iniciando scraping de actividades en Oaxaca desde Booking.com")
    print("📍 Usando la URL específica para Oaxaca de Juárez")
    
    # Configuración
    max_activities = 100  # Número máximo de actividades a extraer
    
    results = scrape_booking_activities_oaxaca(max_activities)
    
    if results:
        print(f"\n🎉 ¡Éxito! Extraídas {len(results)} actividades en Oaxaca")
        print("📋 Puedes encontrar los detalles completos en el archivo JSON generado")
        
    else:
        print("\n❌ No se pudieron extraer actividades")

if __name__ == "__main__":
    main()