import asyncio, random, time
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# --- Configuración ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)... Chrome/131...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)... Safari/605.1.15",
]
RETRIES = 3
RESULTS_LIMIT = 100  # máximo hoteles
COMMENTS_LIMIT = 10  # comentarios por hotel

# --- Helpers ---
def get_random_ua():
    return random.choice(USER_AGENTS)

def build_expedia_url(dest, checkin, checkout):
    return (
        "https://www.expedia.com/Hotel-Search?"
        f"destination={dest}&startDate={checkin}&endDate={checkout}"
        "&adults=1&rooms=1&sort=RECOMMENDED"
    )

# Extrae datos básicos de la tarjeta de hotel
async def parse_card(card):
    href = await card.locator("[data-stid='open-hotel-information']").get_attribute("href") or ""
    print(f"Procesando hotel: {href}")
    return {
        'url': f"https://www.expedia.com{href}",
        'name': await card.locator("h3.uitk-heading").text_content() or "",
        'price': await card.locator("[data-test-id='price-summary'] [data-test-id='price-summary-message-line']:first-of-type div span").text_content() or "",
        'rating': await card.locator("span.uitk-badge-base-large span.is-visually-hidden").text_content() or "",
        'reviews': await card.locator("span.uitk-text.uitk-type-200").text_content() or ""
    }


# Abre la página del hotel y extrae hasta COMMENTS_LIMIT comentarios
async def extract_comments(page, limit=COMMENTS_LIMIT):
    comments = []
    await page.goto(page.url)
    # scroll-pauses para cargar reviews
    for _ in range(5):
        await page.mouse.wheel(0, 1000)
        await asyncio.sleep(random.uniform(1,2))
    # Selecciona los comentarios
    comment_elems = await page.locator("div[data-test-id='review-text']").all()
    for elem in comment_elems[:limit]:
        txt = await elem.text_content()
        comments.append(txt.strip() if txt else "")
    return comments

# Scraper principal
async def scrape(dest, checkin, checkout):
    url = build_expedia_url(dest, checkin, checkout)
    for attempt in range(1, RETRIES+1):
        ua = get_random_ua()
        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True)
                ctx = await browser.new_context(user_agent=ua, locale="en-US")
                page = await ctx.new_page()
                await page.goto(url)
                await asyncio.sleep(random.uniform(3,6))
                # cerrar modal si aparece
                try: 
                    await page.locator("#close-fee-inclusive-pricing-sheet").wait_for(state="visible")
                except PlaywrightTimeout: pass
                cards = await page.locator("[data-stid='lodging-card-responsive']").all()
                print(cards)
                if len(cards) > 2:
                    await cards[2].wait_for(state="visible", timeout=30000)
                else:
                    print("No hay suficientes tarjetas de hotel.")
                await page.locator("[data-stid='lodging-card-responsive']").nth(2).wait_for(state="visible", timeout=10000)

                cards = await page.locator("[data-stid='lodging-card-responsive']").all()
                results = []
                for card in cards[:RESULTS_LIMIT]:
                    entry = await parse_card(card)
                    # extraer comentarios
                    hotel_page = await ctx.new_page()
                    hotel_page.url = entry['url']
                    await hotel_page.goto(entry['url'])
                    await asyncio.sleep(random.uniform(2,4))
                    entry['comments'] = await extract_comments(hotel_page)
                    await hotel_page.close()
                    results.append(entry)
                    await asyncio.sleep(random.uniform(2,5))
                await browser.close()
                return results
        except Exception as e:
            print(f"Error intento {attempt}: {e}, UA: {ua}")
            await asyncio.sleep(5 * attempt)
    raise RuntimeError("Todos los intentos fallaron")

# --- Ejecución ejemplo ---
if __name__ == "__main__":
    destino = "Oaxaca%2C%20Oaxaca%2C%20Mexico"
    checkin = "2025-09-09"
    checkout = "2025-09-10"
    data = asyncio.run(scrape(destino, checkin, checkout))
    print(f"Hoteles extraídos: {len(data)}")
    for h in data:
        print(h['name'], h['comments'][:2], "...")

