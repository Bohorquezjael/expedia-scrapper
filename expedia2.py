from scrapingbee import ScrapingBeeClient
import pandas as pd

client = ScrapingBeeClient(api_key='EK0XY3V9C7ZGN8B9FAL61GCC6HI3J7BCBUEH3410CRWSKATGEQICE3LZKITMCBTHF081EHL72PZUPTC7')

def expedia_search(destination, start_date, end_date):
    extract_rules = {
    "properties": {
        # the chosen selector will iterate over loaded hotel listing cards
        "selector": ".uitk-layout-grid.uitk-layout-grid-has-auto-columns.uitk-layout-grid-has-columns-by-medium.uitk-layout-grid-display-grid",
        "type": "list",
        "output": {
            # within the listing cards, these CSS selectors contain the most relevant information
            "name": "h3.uitk-heading.uitk-heading-5",
            "location": ".uitk-text.uitk-text-spacing-half.truncate-lines-2",
            "price_per_day": "[data-test-id='price-summary'] [data-test-id='price-summary-message-line']:first-of-type div span",
            "rating": "span.uitk-badge.uitk-badge-base-large.uitk-badge-base-has-text > span.is-visually-hidden",
            "reviews": "span.uitk-text.uitk-type-200.uitk-type-regular.uitk-text-default-theme"
        }
    }
}
    js_scenario = {
    "instructions": [
    # Pause for 2 seconds to let the page load
        {"wait": 2000},
    # scroll down to the bottom of the page
        {"evaluate": "window.scrollTo(0, document.body.scrollHeight);"},
        {"wait": 2000}
    # Pause for 2 seconds to let the page load
    ]
    }
    
    q = destination.replace(' ', '+')
    # assigns the GET API call to the response variable 
    response =  client.get(
        f'https://www.expedia.com/Hotel-Search?destination={q}&endDate={end_date}&startDate={start_date}',
# parameters that control how the request is processed and how data is extracted from the loaded page
        params={ 
            "wait_for": ".uitk-layout-grid.uitk-layout-grid-has-auto-columns.uitk-layout-grid-has-columns-by-medium.uitk-layout-grid-display-grid",
            "extract_rules": extract_rules,
            "js_scenario": js_scenario, 
            'country_code':'us'
        },
        retries=2
    )
    
    if response.text.startswith('{"message":"Invalid api key:'):
        return (
            "Oops! It seems you may have missed adding your API KEY or "
            "you are using an incorrect key.\n"
            "You can obtain your API KEY by visiting this page: "
            "https://app.scrapingbee.com/account/manage/api_key"
        )
    else:
        def get_info():
            if len(response.json()['properties']) == 0:
                return "FAILED TO RETRIEVE PROPERTIES"
            else:
                return "SUCCESS"

        props = response.json().get('properties', [])
    #prints the results 
        df = pd.DataFrame(props)
        df.to_json('expedia_results.json', orient='records', force_ascii=False)
        

expedia_search("Oaxaca, México", "2025-09-09", "2025-09-10")