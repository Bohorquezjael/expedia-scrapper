# test_connection.py
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = "https://www.expedia.com/Hotel-Search?destination=Oaxaca%2C%20Oaxaca%2C%20Mexico&startDate=2025-09-09&endDate=2025-09-10&adults=1&rooms=1&sort=RECOMMENDED"

response = requests.get(url, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response Length: {len(response.text)}")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    print("Título de la página:", soup.title.string if soup.title else "No title")
else:
    print("Respuesta:", response.text[:500])