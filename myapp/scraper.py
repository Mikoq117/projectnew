import os
import django
import requests
from bs4 import BeautifulSoup  # For scraping
from myapp.models import PhoneSpecs

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutorial.settings')
django.setup()

HEADERS = {"User-Agent": "Mozilla/5.0"}

def save_phone_specs_to_db(phone_data):
    """
    Save phone specs to the database and detect the platform and device type.
    """
    os_field = phone_data.get("os", "").lower()

    # Determine the platform
    if os_field.startswith("ios") or os_field.startswith("ipados"):
        platform = "iOS"
    elif os_field.startswith("android"):
        platform = "Android"
    else:
        platform = "Unknown"

    # Determine if it's a phone or a tablet
    device_type = phone_data.get("device_type", "Phone")  # Default is phone unless stated otherwise

    phone, created = PhoneSpecs.objects.get_or_create(
        name=phone_data["name"],
        defaults={
            "release_date": phone_data["release_date"],
            "display_size": phone_data["display_size"],
            "os": phone_data["os"],
            "platform": platform,
            "device_type": device_type  # Save detected type (Phone or Tablet)
        }
    )
    if created:
        print(f"Saved: {phone.name} ({platform}, {device_type})")
    else:
        print(f"Already exists: {phone.name} ({platform}, {device_type})")


def fetch_phone_specs(phone_url, device_type="Phone"):
    """
    Fetches the specs of a phone or tablet from its GSMArena page.
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
        "device_type": device_type  # Pass device type to distinguish tablets from phones
    }


def fetch_phone_models(brand_url, device_type="Phone", limit=15):
    """
    Generic function to fetch phone models for a specific brand.
    :param brand_url: URL of the brand page on GSMArena.
    :param device_type: "Phone" or "Tablet" to classify the device.
    :param limit: Limit the number of models to fetch to avoid bans.
    :return: List of phone models.
    """
    print(f"Fetching {device_type}s from: {brand_url}")
    try:
        response = requests.get(brand_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {device_type} brand page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # Selector for phone models
    model_links = soup.select("div.makers ul li a")
    print(f"Found {len(model_links)} {device_type} models.")

    phone_models = []
    for model in model_links[:limit]:
        model_name = model.text.strip()
        model_url = f"https://www.gsmarena.com/{model['href']}"
        phone_models.append({"name": model_name, "url": model_url, "device_type": device_type})
        print(f"Fetched model: {model_name}, URL: {model_url}")

    print(f"Fetched {len(phone_models)} {device_type} models in total.")
    return phone_models


def scrape_samsung():
    """Scrape Samsung phone models and save them as 'Android Phones'."""
    samsung_url = "https://www.gsmarena.com/samsung-phones-9.php"
    print("Starting Samsung scraper...")
    phone_models = fetch_phone_models(samsung_url, device_type="Phone", limit=15)
    for phone in phone_models:
        specs = fetch_phone_specs(phone["url"], device_type="Phone")
        if specs:
            save_phone_specs_to_db(specs)
    print("Samsung scraping completed!")


def scrape_apple():
    """Scrape Apple iPhone models and save them as 'iOS Phones'."""
    apple_url = "https://www.gsmarena.com/apple-phones-48.php"
    print("Starting Apple scraper...")
    phone_models = fetch_phone_models(apple_url, device_type="Phone", limit=15)
    for phone in phone_models:
        specs = fetch_phone_specs(phone["url"], device_type="Phone")
        if specs:
            save_phone_specs_to_db(specs)
    print("Apple scraping completed!")


def scrape_ipads():
    """Scrape Apple iPad models and save them as 'iOS Tablets'."""
    ipad_url = "https://www.gsmarena.com/results.php3?mode=tablet&sMakers=48"
    print("Starting iPad scraper...")
    tablet_models = fetch_phone_models(ipad_url, device_type="Tablet", limit=15)
    for tablet in tablet_models:
        specs = fetch_phone_specs(tablet["url"], device_type="Tablet")
        if specs:
            save_phone_specs_to_db(specs)
    print("iPad scraping completed!")


def scrape_android_tablets():
    """Scrape Android tablet models and save them as 'Android Tablets'."""
    android_tablet_url = "https://www.gsmarena.com/results.php3?mode=tablet&nYearMin=2015&sMakers=9&sAvailabilities=1,3"
    print("Starting Android Tablet scraper...")
    tablet_models = fetch_phone_models(android_tablet_url, device_type="Tablet", limit=15)
    for tablet in tablet_models:
        specs = fetch_phone_specs(tablet["url"], device_type="Tablet")
        if specs:
            save_phone_specs_to_db(specs)
    print("Android Tablet scraping completed!")


def scrape_all():
    """Scrape both phones and tablets."""
    scrape_samsung()
    scrape_apple()
    scrape_ipads()
    scrape_android_tablets()


if __name__ == "__main__":
    scrape_all()
