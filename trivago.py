from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
import csv
from datetime import datetime

class TrivagoScraper:
    def __init__(self):
        # Configurar opciones de Chrome
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 15)
        
    def close_cookies_popup(self):
        """Cierra el popup de cookies si aparece"""
        try:
            cookie_selectors = [
                "button#onetrust-accept-btn-handler",
                "button.trv_gdpr-consent-button",
                "button[aria-label='Aceptar cookies']",
                "button[data-testid='accept-cookies-button']",
                "button:contains('Aceptar')",
                "button:contains('Accept')"
            ]
            
            for selector in cookie_selectors:
                try:
                    cookie_button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    cookie_button.click()
                    print("Popup de cookies cerrado")
                    time.sleep(1)
                    return True
                except:
                    continue
                    
        except Exception as e:
            print(f"No se pudo cerrar popup de cookies: {e}")
            return False

    def clear_search_field(self):
        """Limpia completamente el campo de búsqueda"""
        try:
            # Encontrar el campo de búsqueda
            search_input = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[data-testid='search-form-destination']"))
            )
            
            # Hacer clic y seleccionar todo el texto
            search_input.click()
            time.sleep(1)
            
            # Seleccionar todo el texto y borrarlo
            search_input.send_keys(Keys.CONTROL + "a")
            time.sleep(0.5)
            search_input.send_keys(Keys.DELETE)
            time.sleep(1)
            
            # Verificar que esté vacío
            if search_input.get_attribute('value'):
                print("El campo aún tiene texto, intentando limpiar de otra manera...")
                search_input.clear()
                time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"Error limpiando campo de búsqueda: {e}")
            return False
    
    def search_destination(self, destination):
        """Realiza la búsqueda de un destino"""
        try:
            # Ir a trivago México
            print(f"Navegando a trivago.com.mx...")
            self.driver.get("https://www.trivago.com.mx")
            time.sleep(3)
            
            # Cerrar popup de cookies
            self.close_cookies_popup()
            
            # Limpiar completamente el campo de búsqueda
            if not self.clear_search_field():
                print("No se pudo limpiar el campo de búsqueda")
                return False
            
            # Escribir el nuevo destino
            search_input = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[data-testid='search-form-destination']"))
            )
            
            print(f"Escribiendo destino: {destination}")
            for char in destination:
                search_input.send_keys(char)
                time.sleep(0.1)
            
            time.sleep(2)  # Esperar sugerencias
            
            # Seleccionar la primera sugerencia
            try:
                first_suggestion = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='search-suggestion']:first-child"))
                )
                first_suggestion.click()
                print("Primera sugerencia seleccionada")
                time.sleep(1)
            except:
                print("Usando ENTER para buscar")
                search_input.send_keys(Keys.ENTER)
            
            # Hacer clic en el botón de búsqueda
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='search-button-with-loader']"))
            )
            search_button.click()
            print("Búsqueda iniciada")
            
            # Esperar resultados
            time.sleep(5)
            return True
            
        except Exception as e:
            print(f"Error al buscar destino {destination}: {str(e)}")
            return False

    def extract_review_summary(self, hotel_element):
        """Extrae el resumen de reseñas haciendo clic en el hotel y luego en opiniones"""
        try:
            # Guardar el contexto actual (página de resultados)
            original_window = self.driver.current_window_handle
            
            # Hacer clic en el nombre del hotel para abrir detalles
            hotel_name_button = hotel_element.find_element(By.CSS_SELECTOR, "button[data-testid='item-name']")
            hotel_name_button.click()
            print("Abriendo detalles del hotel...")
            time.sleep(3)
            
            # Buscar y hacer clic en la pestaña de opiniones
            try:
                reviews_tab = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-selected='false'][data-testid*='REVIEW']"))
                )
                reviews_tab.click()
                print("Haciendo clic en pestaña de opiniones...")
                time.sleep(3) 
            except:
                print("No se encontró pestaña de opiniones")
                # Cerrar el panel de detalles
                self.close_hotel_details()
                return "No disponible"
            
            # Extraer el resumen de reseñas
            review_summary = "No disponible"
            try:
                # Intentar encontrar el resumen completo
                summary_selectors = [
                    "[data-testid='reviews-summary-text']",
                    ".review-summary",
                    "[itemprop='description']",
                    ".summary-text"
                ]
                
                for selector in summary_selectors:
                    try:
                        summary_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        review_summary = summary_element.text.strip()
                        if review_summary:
                            break
                    except:
                        continue
                
                # Si hay botón "ver más", hacer clic y obtener texto completo
                try:
                    see_more_button = self.driver.find_element(By.CSS_SELECTOR, "button:contains('Ver más'), button:contains('See more')")
                    see_more_button.click()
                    time.sleep(1)
                    # Volver a extraer el texto completo
                    for selector in summary_selectors:
                        try:
                            summary_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            review_summary = summary_element.text.strip()
                            break
                        except:
                            continue
                except:
                    pass
                    
            except Exception as e:
                print(f"Error extrayendo resumen: {e}")
            
            # Cerrar el panel de detalles
            self.close_hotel_details()
            
            return review_summary
            
        except Exception as e:
            print(f"Error extrayendo reseñas: {e}")
            # Intentar cerrar el panel si está abierto
            try:
                self.close_hotel_details()
            except:
                pass
            return "Error al extraer"

    def close_hotel_details(self):
        """Cierra el panel de detalles del hotel"""
        try:
            close_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-testid='slideout-x-button']")
            close_button.click()
            time.sleep(2)
        except:
            # Si no se puede cerrar con el botón, intentar con ESC
            try:
                from selenium.webdriver.common.keys import Keys
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(1)
            except:
                pass

    def extract_hotel_data(self, hotel_element):
        """Extrae datos de un elemento de hotel incluyendo reseñas"""
        try:
            # Nombre del hotel
            name = "No disponible"
            try:
                name_element = hotel_element.find_element(By.CSS_SELECTOR, "button[data-testid='item-name'] span")
                name = name_element.get_attribute("title") or name_element.text
            except:
                pass
            
            # Precio
            price = "No disponible"
            try:
                price_element = hotel_element.find_element(By.CSS_SELECTOR, "[data-testid='recommended-price']")
                price = price_element.text.strip()
            except:
                pass
            
            # Calificación
            rating = "No disponible"
            try:
                rating_elements = hotel_element.find_elements(By.CSS_SELECTOR, "[itemprop='ratingValue']")
                rating = rating_elements[1].get_attribute('content')
            except:
                pass
            
            # URL
            url = "No disponible"
            try:
                # Intentar obtener URL del botón del nombre
                name_button = hotel_element.find_element(By.CSS_SELECTOR, "button[data-testid='item-name']")
                url = name_button.get_attribute('href')
                
                # Si no tiene href, intentar construir la URL desde data attributes
                if not url or url == "No disponible":
                    try:
                        hotel_id = hotel_element.get_attribute('data-accommodation')
                        if hotel_id:
                            url = f"https://www.trivago.com.mx/es-mx/odr/hoteles-mexico?search=200-{hotel_id}"
                    except:
                        pass
            except:
                pass
            
            # Extraer resumen de reseñas
            print(f"Extrayendo reseñas para: {name}")
            review_summary = self.extract_review_summary(hotel_element)
            
            return {
                "nombre": name,
                "precio": price,
                "calificacion": rating,
                "url": url,
                "resena": review_summary,
                "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"Error extrayendo datos: {str(e)}")
            return None

    def scrape_page(self):
        """Extrae datos de la página actual"""
        hotels_data = []
        
        try:
            # Esperar a que carguen los hoteles
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='accommodation-list-element']"))
            )
            
            hotel_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='accommodation-list-element']")
            print(f"Encontrados {len(hotel_elements)} hoteles en la página")
            
            for i, hotel_element in enumerate(hotel_elements):
                try:
                    print(f"Procesando hotel {i+1} de {len(hotel_elements)}...")
                    hotel_data = self.extract_hotel_data(hotel_element)
                    if hotel_data:
                        hotels_data.append(hotel_data)
                        print(f"✓ {hotel_data['nombre']} - {hotel_data['precio']}")
                    time.sleep(2)  # Pausa entre hoteles
                except Exception as e:
                    print(f"Error procesando hotel {i+1}: {e}")
                    continue
            
        except Exception as e:
            print(f"Error en scrape_page: {str(e)}")
        
        return hotels_data

    def go_to_next_page(self):
        """Intenta ir a la siguiente página"""
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-testid='next-page']")
            
            if next_button.is_enabled():
                self.driver.execute_script("arguments[0].scrollIntoView();", next_button)
                time.sleep(1)
                next_button.click()
                print("Yendo a la siguiente página...")
                time.sleep(3)
                return True
            else:
                return False
                
        except:
            return False

    def scrape_destination(self, destination, max_pages=2):
        """Scrapea un destino completo"""
        print(f"\n{'='*50}")
        print(f"Iniciando scrape para: {destination}")
        
        if not self.search_destination(destination):
            return []
        
        all_hotels = []
        current_page = 1
        
        while current_page <= max_pages:
            print(f"\n--- Extrayendo página {current_page} ---")
            
            page_data = self.scrape_page()
            all_hotels.extend(page_data)
            
            print(f"Encontrados {len(page_data)} hoteles en página {current_page}")
            
            if current_page < max_pages:
                if not self.go_to_next_page():
                    break
            
            current_page += 1
        
        print(f"Scrape completado para {destination}. Total: {len(all_hotels)} hoteles")
        return all_hotels
    
    def save_to_csv(self, data, filename):
        """Guarda los datos en CSV"""
        if not data:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['nombre', 'precio', 'calificacion', 'url', 'resena', 'fecha_extraccion']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in data:
                    writer.writerow(row)
            
            print(f"Datos guardados en {filename}")
            
        except Exception as e:
            print(f"Error guardando CSV: {str(e)}")
    
    def close(self):
        """Cierra el navegador"""
        self.driver.quit()

# Lista de destinos
destinos = [
    "Cancún",
    "Ciudad de México",
    "Guadalajara"
]

def main():
    scraper = TrivagoScraper()
    
    try:
        all_data = []
        
        for destino in destinos:
            destino_data = scraper.scrape_destination(destino, max_pages=1)
            all_data.extend(destino_data)
            time.sleep(3)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"trivago_data_{timestamp}.csv"
        scraper.save_to_csv(all_data, filename)
        
        print(f"\nProceso completado. Total de hoteles: {len(all_data)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.close()

if __name__ == "__main__":
    main()