import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains

# Configuración Selenium
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# Lista de ubicaciones a buscar
locations = ["Oaxaca", "Guadalajara"]

def smooth_scroll_with_pauses(driver, total_scrolls=1, scroll_step=600, pause_time=2.0):
    """
    Scroll suave con pausas para cargar contenido gradualmente
    """
    for i in range(total_scrolls):
        driver.execute_script(f"""
            window.scrollBy({{
                top: {scroll_step},
                behavior: 'smooth'
            }});
        """)
        
        print(f"Scroll {i+1} - Avanzando {scroll_step}px")
        time.sleep(pause_time)
        
        current_position = driver.execute_script("return window.pageYOffset;")
        total_height = driver.execute_script("return document.body.scrollHeight;")
        window_height = driver.execute_script("return window.innerHeight;")
        
        if current_position + window_height >= total_height:
            print("Llegado al final de la página")
            break

def collect_restaurant_urls(driver, max_scrolls=30):
    """
    Colecciona URLs de restaurantes recolectando durante el scroll
    """
    all_urls = set()
    scroll_count = 0
    no_new_count = 0
    
    # Esperar a que carguen los primeros resultados
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-test='res-card-name']"))
        )
    except TimeoutException:
        print("No se encontraron restaurantes")
        return list(all_urls)

    while scroll_count < max_scrolls and no_new_count < 5:
        try:
            # Obtener URLs actuales
            current_urls = set()
            restaurant_links = driver.find_elements(By.CSS_SELECTOR, "a[data-test='res-card-name']")
            
            for link in restaurant_links:
                try:
                    href = link.get_attribute("href")
                    if href:
                        current_urls.add(href)
                except StaleElementReferenceException:
                    continue
            
            # Verificar cuántos URLs nuevos encontramos
            new_urls = current_urls - all_urls
            if new_urls:
                all_urls.update(new_urls)
                print(f"Scroll {scroll_count + 1}: +{len(new_urls)} nuevos, Total: {len(all_urls)}")
                no_new_count = 0
            else:
                no_new_count += 1
                print(f"Scroll {scroll_count + 1}: Sin nuevos elementos ({no_new_count}/5)")
            
            # Hacer scroll si no hemos llegado al final
            if no_new_count < 5:
                smooth_scroll_with_pauses(driver, total_scrolls=1, scroll_step=600, pause_time=2.0)
            
            scroll_count += 1
            
            # Verificar si llegamos al final
            current_position = driver.execute_script("return window.pageYOffset;")
            total_height = driver.execute_script("return document.body.scrollHeight;")
            if current_position + 1000 >= total_height:
                print("Final de página detectado")
                break
                
        except Exception as e:
            print(f"Error durante el scroll: {e}")
            break
    
    print(f"Scrolling completado. Total único: {len(all_urls)} restaurantes")
    return list(all_urls)

def extract_reviews(driver):
    """
    Extrae las reseñas usando los selectores específicos de la imagen
    """
    reviews = []
    
    try:
        # Esperar a que carguen las reseñas
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-test='reviews-list-item']"))
        )
        
        # Encontrar todos los elementos de reseña
        review_elements = driver.find_elements(By.CSS_SELECTOR, "li[data-test='reviews-list-item']")
        print(f"Encontrados {len(review_elements)} elementos de reseña")
        
        for review_element in review_elements:
            try:
                review_data = {
                    "nombre": "",
                    "pais": "",
                    "reseñas_totales": "",
                    "puntuacion_estrellas": "",
                    "puntuacion_valor": "",
                    "fecha_visita": "",
                    "comentario": "",
                    "subclasificaciones": {}
                }
                
                # Extraer nombre del reviewer - Selector de la imagen: p.RUDCRcUiZIA-
                try:
                    name_element = review_element.find_element(By.CSS_SELECTOR, "p.RUDCRcUiZIA-")
                    review_data["nombre"] = name_element.text.strip()
                except:
                    try:
                        # Fallback: buscar en toda la estructura del nombre
                        name_element = review_element.find_element(By.CSS_SELECTOR, "[data-test*='reviewer-name'], .reviewer-name")
                        review_data["nombre"] = name_element.text.strip()
                    except:
                        pass
                
                # Extraer país - Selector de la imagen: span.KiLDx3Qnn7l-
                try:
                    country_element = review_element.find_element(By.CSS_SELECTOR, "span.KiLDx3Qnn7l-")
                    review_data["pais"] = country_element.text.strip()
                except:
                    pass
                
                # Extraer número de reseñas totales del usuario
                try:
                    # Buscar el texto que contiene "reseña" después del país
                    review_count_text = review_element.find_element(By.CSS_SELECTOR, "p.H-LuDvpOa3g-").text
                    if "reseña" in review_count_text:
                        review_data["reseñas_totales"] = review_count_text
                except:
                    pass
                
                # Extraer puntuación de estrellas - Selector de la imagen: div.yEKDnyk-7-g-[aria-label]
                try:
                    stars_element = review_element.find_element(By.CSS_SELECTOR, "div.yEKDnyk-7-g-")
                    aria_label = stars_element.get_attribute("aria-label")
                    if aria_label:
                        review_data["puntuacion_estrellas"] = aria_label
                except:
                    pass
                
                # Extraer valor numérico de puntuación - Selector de la imagen: div.t51WYQ89es0-
                try:
                    rating_value_element = review_element.find_element(By.CSS_SELECTOR, "div.t51WYQ89es0-")
                    review_data["puntuacion_valor"] = rating_value_element.text.strip()
                except:
                    pass
                
                # Extraer fecha de visita - Selector de la imagen: p.ilkfeQbexGs-
                try:
                    date_element = review_element.find_element(By.CSS_SELECTOR, "p.ilkfeQbexGs-")
                    review_data["fecha_visita"] = date_element.text.strip()
                except:
                    pass
                
                # Extraer comentario - Selector de la imagen: span[data-test='wrapper-tag']
                try:
                    comment_element = review_element.find_element(By.CSS_SELECTOR, "span[data-test='wrapper-tag']")
                    review_data["comentario"] = comment_element.text.strip()
                except:
                    try:
                        # Fallback para comentario
                        comment_element = review_element.find_element(By.CSS_SELECTOR, "[data-test*='review-text'], .review-text")
                        review_data["comentario"] = comment_element.text.strip()
                    except:
                        pass
                
                # Extraer subclasificaciones - Selector de la imagen: li.k5xpff5Xac-
                try:
                    sub_rating_elements = review_element.find_elements(By.CSS_SELECTOR, "li.k5xpff5Xac-")
                    for sub_element in sub_rating_elements:
                        try:
                            text = sub_element.text.strip()
                            if text:
                                # Las subclasificaciones suelen tener formato "Categoría X.X"
                                review_data["subclasificaciones"][f"categoria_{len(review_data['subclasificaciones']) + 1}"] = text
                        except:
                            continue
                except:
                    pass
                
                # Solo agregar la reseña si tiene al menos algún dato
                if any(value for key, value in review_data.items() if key != 'subclasificaciones'):
                    reviews.append(review_data)
                    print(f"✓ Reseña de {review_data['nombre']} extraída")
                
            except Exception as e:
                print(f"Error extrayendo reseña individual: {e}")
                continue
                
    except TimeoutException:
        print("No se encontraron reseñas con el selector li[data-test='reviews-list-item']")
    except Exception as e:
        print(f"Error general extrayendo reseñas: {e}")
    
    return reviews

# Resultado final
data = {}

for location in locations:
    print(f"\n{'='*60}")
    print(f"🚀 BUSCANDO EN: {location}")
    print(f"{'='*60}")
    
    driver.get("https://www.opentable.com.mx/")
    time.sleep(2)

    # Manejar cookies
    try:
        accept_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label*='ceptar'], button[aria-label*='ccept']"))
        )
        accept_btn.click()
        print("✅ Cookies aceptadas")
        time.sleep(1)
    except TimeoutException:
        print("ℹ️ No se encontró botón de cookies")
    
    # Realizar búsqueda
    try:
        search_box = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='search'], #home-page-autocomplete-input"))
        )
        search_box.clear()
        search_box.send_keys(location)
        time.sleep(2)
        
        # Intentar seleccionar sugerencia
        try:
            suggestions = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.autocomplete-results li, .autocomplete-item"))
            )
            if suggestions:
                suggestions[0].click()
                print("✅ Sugerencia seleccionada")
            else:
                search_box.send_keys(Keys.ENTER)
                print("✅ Búsqueda con ENTER")
        except:
            search_box.send_keys(Keys.ENTER)
            print("✅ Búsqueda con ENTER (fallback)")
        
        # Esperar resultados
        print("⏳ Esperando resultados de búsqueda...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-test='res-card-name'], .restaurant-card, [data-test*='restaurant']"))
        )
        
        time.sleep(4)

        # Coleccionar URLs
        print("\n🔄 Iniciando scroll controlado...")
        restaurant_urls = collect_restaurant_urls(driver)
        
        print(f"\n✅ TOTAL ENCONTRADO EN {location}: {len(restaurant_urls)} restaurantes")
        
        if not restaurant_urls:
            print(f"❌ No se encontraron restaurantes en {location}")
            continue

        data[location] = []
        
        # Procesar restaurantes (limitar a 3 para demo)
        max_restaurants = min(3, len(restaurant_urls))
        for i, url in enumerate(restaurant_urls[:max_restaurants]):
            print(f"\n🔍 Procesando restaurante {i+1}/{max_restaurants}")
            print(f"🌐 URL: {url}")
            
            try:
                driver.get(url)
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                time.sleep(4)

                # Extraer información básica del restaurante
                info = {
                    "nombre": "No disponible",
                    "ubicacion": "No disponible",
                    "puntuacion_general": "No disponible",
                    "tipo_comida": "No disponible",
                    "url": url,
                    "reseñas": []
                }

                # Nombre
                try:
                    name_element = driver.find_element(By.CSS_SELECTOR, "h1, .restaurant-name, [data-test*='restaurant-name']")
                    info["nombre"] = name_element.text
                except:
                    pass

                # Dirección
                try:
                    address_element = driver.find_element(By.CSS_SELECTOR, "div._1xxAN, .restaurant-address, address, [data-test*='address']")
                    info["ubicacion"] = address_element.text
                except:
                    pass

                # Rating general
                try:
                    rating_element = driver.find_element(By.CSS_SELECTOR, "div._3ce0j, .overall-rating, [data-test*='overall-rating']")
                    info["puntuacion_general"] = rating_element.text
                except:
                    pass

                # Tipo de comida
                try:
                    cuisine_element = driver.find_element(By.CSS_SELECTOR, "div._2crCz, .cuisine-type, [data-test*='cuisine']")
                    info["tipo_comida"] = cuisine_element.text
                except:
                    pass

                # Extraer reseñas con los selectores específicos
                print("📖 Extrayendo reseñas...")
                info["reseñas"] = extract_reviews(driver)

                print(f"✅ Nombre: {info['nombre']}")
                print(f"📍 Dirección: {info['ubicacion']}")
                print(f"⭐ Rating General: {info['puntuacion_general']}")
                print(f"🍽️ Tipo: {info['tipo_comida']}")
                print(f"📝 Reseñas extraídas: {len(info['reseñas'])}")

                data[location].append(info)

            except Exception as e:
                print(f"❌ Error procesando restaurante: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Error en búsqueda de {location}: {e}")
        continue

# Guardar resultados
try:
    with open("opentable_reviews_detailed.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"\n💾 Resultados guardados en opentable_reviews_detailed.json")
except Exception as e:
    print(f"❌ Error guardando archivo: {e}")

print(f"\n{'='*60}")
print("🎉 EXTRACCIÓN DE RESEÑAS COMPLETADA!")
print(f"{'='*60}")

driver.quit()