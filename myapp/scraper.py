import os
import django
import requests
from bs4 import BeautifulSoup #needed for scraping
from myapp.models import PhoneSpecs  # Import the PhoneSpecs model


# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutorial.settings')
django.setup()

HEADERS = {"User-Agent": "Mozilla/5.0"}

def save_phone_specs_to_db(phone_data):
    #Save phone specs to the database,
    phone, created = PhoneSpecs.objects.get_or_create(
        name=phone_data["name"],  # Check by unique phone name
        defaults={
            "release_date": phone_data["release_date"],
            "display_size": phone_data["display_size"],
            "os": phone_data["os"],
        }
    )
    if created:
        print(f"Saved: {phone.name}")
    else:
        print(f"Already exists: {phone.name}")


def fetch_phone_specs(phone_url):
  #gets specs from GSMarena
    try:
        print(f"Fetching specs for: {phone_url}")
        response = requests.get(phone_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {phone_url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Fetch the release date
    release_date = "Not available"
    release_element = soup.select_one("td.nfo[data-spec='year']")
    if release_element:
        release_date = release_element.text.strip()

    # Fetch display size
    display_size = "Not available"
    display_element = soup.select_one("td.nfo[data-spec='displaysize']")
    if display_element:
        full_display_text = display_element.text.strip()
        display_size = full_display_text[:11]  # Take only the first 11 characters

    # Fetch OS
    os = "Not available"
    os_element = soup.select_one("td.nfo[data-spec='os']")
    if os_element:
        os = os_element.text.strip()

    return {
        "name": soup.select_one("h1").text.strip() if soup.select_one("h1") else "Unknown",
        "release_date": release_date,
        "display_size": display_size,
        "os": os,
    }

#temporarily just fetching some smansung phones
def fetch_phone_models():
    print("Fetching Samsung phones from GSMArena...")
    base_url = "https://www.gsmarena.com"
    samsung_url = f"{base_url}/samsung-phones-9.php"  # Samsung's dedicated page on GSMArena

    try:
        response = requests.get(samsung_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        print(response.text[:500])  # Debugging: print the first 500 characters
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Samsung page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # Selector for Samsung phone models
    model_links = soup.select("div.makers ul li a")
    print(f"Found {len(model_links)} Samsung phone models.")  # Debugging

    phone_models = []
    for model in model_links[:15]:  # Limit to 15 models
        model_name = model.text.strip()
        model_url = f"{base_url}/{model['href']}"
        phone_models.append({"name": model_name, "url": model_url})
        print(f"Fetched model: {model_name}, URL: {model_url}")  # Debugging

    print(f"Fetched {len(phone_models)} Samsung phone models in total.")
    return phone_models

#scraping

def scrape():
    print("Starting scraper...")
    phone_models = fetch_phone_models()
    for phone in phone_models:
        phone_name = phone["name"]
        phone_url = phone["url"]
        print(f"Fetching specs for {phone_name}...")
        specs = fetch_phone_specs(phone_url)
        if specs:
            save_phone_specs_to_db(specs)
    print(f"Scraping completed! Total phones in database: {PhoneSpecs.objects.count()}")


if __name__ == "__main__":
    scrape()
