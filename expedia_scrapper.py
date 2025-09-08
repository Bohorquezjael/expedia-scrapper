import time
import csv
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- Función para Manejar Pop-ups de Expedia ---
def handle_expedia_popups(driver, wait):
    """
    Busca y cierra varios tipos de ventanas emergentes que aparecen en Expedia.
    """
    popup_selectors = [
        "button[aria-label='Cerrar']",
        "button.uitk-modal-dismiss",
        "div.uitk-modal button.uitk-button",
        "button[data-stid='close-button']"
    ]
    
    for selector in popup_selectors:
        try:
            close_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            print("Popup encontrado. Cerrando...")
            close_button.click()
            time.sleep(1)
        except (TimeoutException, NoSuchElementException):
            continue

# --- Función para Manejar Pop-up de Traducción ---
def handle_translation_popup(driver, short_wait):
    """
    Busca y cierra la ventana emergente de traducción si aparece.
    """
    try:
        close_button_selector = "button.c7pvyrs"
        close_button = short_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, close_button_selector)))
        print("Ventana de traducción encontrada. Cerrándola...")
        close_button.click()
        time.sleep(1)
    except TimeoutException:
        print("Ventana de traducción no encontrada, continuando...")

# --- Funciones para Guardar Archivos ---
def guardar_csv(datos, destino, archivo="expedia_data.csv"):
    """Guarda los datos de los hoteles en un archivo CSV."""
    print(f"\nGuardando {len(datos)} registros en {archivo}...")
    try:
        with open(archivo, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['destino', 'tipo', 'titulo', 'rating', 'comentario', 'url']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for dato in datos:
                fila = {'destino': destino, 'tipo': 'Hotel', **dato}
                writer.writerow(fila)
        print("✅ Guardado en CSV completado.")
    except Exception as e:
        print(f"❌ Error al guardar en CSV: {e}")

def guardar_json(datos, archivo="expedia_data.json"):
    """Guarda los datos de los hoteles en un archivo JSON."""
    print(f"Guardando {len(datos)} registros en {archivo}...")
    try:
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        print("✅ Guardado en JSON completado.")
    except Exception as e:
        print(f"❌ Error al guardar en JSON: {e}")

# --- Configuración de Selenium ---
service = Service()
options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
options.add_argument('accept-language=es-MX,es;q=0.9')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(service=service, options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

wait = WebDriverWait(driver, 20)
wait_short = WebDriverWait(driver, 5)

# --- Lógica de Extracción ---
hoteles_extraidos = []
destino = "oaxaca"

try:
    # PASO 1: Navegar a la página de búsqueda
    url_busqueda = "https://www.expedia.mx/Hotel-Search?rfrr=hotel.search&GOTO=HOTSEARCH&SearchType=Place&SearchArea=City&lang=2058&needUTF8Decode=true&regionId=11175&selected=&latLong=&children=&adults=1&openPlayBack=true&startDate=2025-09-05&endDate=2025-09-06&sort=RECOMMENDED&destination=Oaxaca%2C%20M%C3%A9xico&theme=&userIntent=&semdtl=&categorySearch=&useRewards=false"
    print(f"--- INICIANDO SCRAPING DE HOTELES ---")
    print(f"Navegando a la URL de hoteles: {url_busqueda}")
    driver.get(url_busqueda)
    
    # Manejar pop-ups de Expedia
    handle_expedia_popups(driver, wait_short)
    
    # Esperar a que carguen los resultados
    time.sleep(3)

    # PASO 2: Extraer todos los enlaces de los hoteles
    print("Recopilando los enlaces de los hoteles...")
    
    # Selector actualizado para Expedia
    card_selector = 'a[data-stid="open-hotel-information"]'
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, card_selector)))
    time.sleep(2)
    
    cards = driver.find_elements(By.CSS_SELECTOR, card_selector)
    num_a_extraer = 3
    links = [card.get_attribute('href') for card in cards[:num_a_extraer]]
    print(f"Se encontraron {len(links)} enlaces de hoteles. Empezando la extracción detallada...")

    # PASO 3: Iterar sobre la lista de enlaces
    for i, link in enumerate(links):
        print(f"\n--- Extrayendo Hotel #{i+1} ---")
        print(f"Navegando a: {link}")
        driver.get(link)
        
        # Manejar pop-ups
        handle_expedia_popups(driver, wait_short)
        handle_translation_popup(driver, wait_short)
        
        # Extraer información del hotel
        try:
            # Título del hotel
            titulo = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "h1.uitk-heading"))).text
        except TimeoutException:
            try:
                titulo = driver.find_element(By.TAG_NAME, 'h1').text
            except:
                titulo = "No se pudo encontrar el título"
        
        # Rating
        try:
            rating = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "span[data-testid='rating-badge']"))).text
        except Exception:
            rating = "Sin calificación"
        
        # Comentario o descripción
        try:
            comentario = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[data-stid='content-hotel-reviews'] p.uitk-text"))).text
        except Exception:
            try:
                comentario = driver.find_element(By.CSS_SELECTOR, "div.hotel-description p").text
            except:
                comentario = "No se encontró comentario destacado"

        print(f"  Título: {titulo}")
        print(f"  Rating: {rating}")
        print(f"  Comentario: {comentario}")
        
        hoteles_extraidos.append({
            "titulo": titulo,
            "rating": rating,
            "comentario": comentario,
            "url": link
        })
        
        # Volver a la página de resultados
        if i < len(links) - 1:
            driver.back()
            time.sleep(2)
            handle_expedia_popups(driver, wait_short)
    
    if hoteles_extraidos:
        guardar_csv(hoteles_extraidos, destino, "expedia_data.csv")
        guardar_json(hoteles_extraidos, "expedia_data.json")
    else:
        print("No se extrajeron datos de hoteles, no se guardará ningún archivo.")

finally:
    print("\nProceso completado. Cerrando el navegador.")
    driver.quit()