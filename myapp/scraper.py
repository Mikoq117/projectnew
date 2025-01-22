import os
import django
import requests
from bs4 import BeautifulSoup  # For scraping
from myapp.models import PhoneSpecs


  # Import the PhoneSpecs model

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutorial.settings')
django.setup()

HEADERS = {"User-Agent": "Mozilla/5.0"}

def save_phone_specs_to_db(phone_data):
    """
    Save phone specs to the database, automatically detecting the platform based on the OS field.
    """
    # Infer platform from the "os" field
    os_field = phone_data.get("os", "").lower()  # Use .get() to avoid KeyError
    if os_field.startswith("ios"):
        platform = "iOS"
    elif os_field.startswith("android"):
        platform = "Android"
    else:
        platform = "Unknown"  # Default if the OS field doesn't contain expected values

    phone, created = PhoneSpecs.objects.get_or_create(
        name=phone_data["name"],  # Check by unique phone name
        defaults={
            "release_date": phone_data["release_date"],
            "display_size": phone_data["display_size"],
            "os": phone_data["os"],
            "platform": platform,  # Save the detected platform
        }
    )
    if created:
        print(f"Saved: {phone.name} ({platform})")
    else:
        print(f"Already exists: {phone.name} ({platform})")



def fetch_phone_specs(phone_url):
    """
    Fetches the specs of a phone from its GSMArena page.
    """
    try:
        print(f"Fetching specs for: {phone_url}")
        response = requests.get(phone_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {phone_url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Fetch the release date
    release_date = soup.select_one("td.nfo[data-spec='year']").text.strip() if soup.select_one("td.nfo[data-spec='year']") else "Not available"

    # Fetch display size
    display_size = soup.select_one("td.nfo[data-spec='displaysize']").text.strip()[:11] if soup.select_one("td.nfo[data-spec='displaysize']") else "Not available"

    # Fetch OS
    os = soup.select_one("td.nfo[data-spec='os']").text.strip() if soup.select_one("td.nfo[data-spec='os']") else "Not available"

    return {
        "name": soup.select_one("h1").text.strip() if soup.select_one("h1") else "Unknown",
        "release_date": release_date,
        "display_size": display_size,
        "os": os,
    }


def fetch_phone_models(brand_url, limit=15):
    """
    Generic function to fetch phone models for a specific brand.
    :param brand_url: URL of the brand's page on GSMArena.
    :param limit: Limit the number of models to fetch.
    :return: List of phone models.
    """
    print(f"Fetching phones from: {brand_url}")
    try:
        response = requests.get(brand_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching brand page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # Selector for phone models
    model_links = soup.select("div.makers ul li a")
    print(f"Found {len(model_links)} phone models.")  # Debugging

    phone_models = []
    for model in model_links[:limit]:
        model_name = model.text.strip()
        model_url = f"https://www.gsmarena.com/{model['href']}"
        phone_models.append({"name": model_name, "url": model_url})
        print(f"Fetched model: {model_name}, URL: {model_url}")  # Debugging

    print(f"Fetched {len(phone_models)} phone models in total.")
    return phone_models


def scrape_samsung():
    """
    Scrape Samsung phone models and save them to the database with platform='Android'.
    """
    samsung_url = "https://www.gsmarena.com/samsung-phones-9.php"
    print("Starting Samsung scraper...")
    phone_models = fetch_phone_models(samsung_url, limit=15)
    for phone in phone_models:
        specs = fetch_phone_specs(phone["url"])
        if specs:
            save_phone_specs_to_db(specs) # Pass platform='Android'
    print("Samsung scraping completed!")



def scrape_apple():
    """
    Scrape Apple iPhone models and save them to the database with platform='iOS'.
    """
    apple_url = "https://www.gsmarena.com/apple-phones-48.php"
    print("Starting Apple scraper...")
    phone_models = fetch_phone_models(apple_url, limit=15)
    for phone in phone_models:
        specs = fetch_phone_specs(phone["url"])
        if specs:
            save_phone_specs_to_db(specs)  # Pass platform='iOS'
    print("Apple scraping completed!")


def scrape_all():
    """
    Scrape both Samsung and Apple models.
    """
    scrape_samsung()
    scrape_apple()


if __name__ == "__main__":
    scrape_all()
