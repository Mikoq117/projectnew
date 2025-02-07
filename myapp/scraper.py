import os
import django
import requests
from bs4 import BeautifulSoup  # For scraping
from myapp.models import PhoneSpecs


  # Import the PhoneSpecs model

"""
Scraper currently set to only scrape the first 15 devices on each pages. 
Increasing this alot will result in a temp block from GSMArena, so leave as 15 if your just testing!

Next iteration will only fetch phones so that watches and tablets will not be scraped, then amount can be turned up
"""

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutorial.settings')
django.setup()

HEADERS = {"User-Agent": "Mozilla/5.0"}

def save_phone_specs_to_db(phone_data):
    """
    Save phone specs to the database, and detecting the platform based on the OS field.
    """
    # platfrom check
    os_field = phone_data.get("os", "").lower()  # avoid error
    if os_field.startswith("ios"):
        platform = "iOS"
    elif os_field.startswith("android"):
        platform = "Android"
    else:
        platform = "Unknown"  # Default for weird entries

    phone, created = PhoneSpecs.objects.get_or_create(
        name=phone_data["name"],  # Check by unique phone name
        defaults={
            "release_date": phone_data["release_date"],
            "display_size": phone_data["display_size"],
            "os": phone_data["os"],
            "platform": platform,  # Save  detected platform
        }
    )
    if created:
        print(f"Saved: {phone.name} ({platform})")
    else:
        print(f"Already exists: {phone.name} ({platform})")

#SCRAPING!!

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
    :param brand_url: URL of the brand page on GSMArena.
    :param limit: Limit the number of models to fetch. - IMPORTANT TO NOT BE BLOCKED BY GSM
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
    print(f"Found {len(model_links)} phone models.")  # DebuggGGG

    phone_models = []
    for model in model_links[:limit]:
        model_name = model.text.strip()
        model_url = f"https://www.gsmarena.com/{model['href']}"
        phone_models.append({"name": model_name, "url": model_url})
        print(f"Fetched model: {model_name}, URL: {model_url}")  # Debug

    print(f"Fetched {len(phone_models)} phone models in total.")
    return phone_models


def scrape_samsung():
    """
    Scrape Samsung phone models and save them to the database AS ANDROIDS

    """
    samsung_url = "https://www.gsmarena.com/samsung-phones-9.php"
    print("Starting Samsung scraper...")
    phone_models = fetch_phone_models(samsung_url, limit=15)  #LIMIT CAN BE CHANGED BUT BE CAREFUL
    for phone in phone_models:
        specs = fetch_phone_specs(phone["url"])
        if specs:
            save_phone_specs_to_db(specs) # Pass platform='Android'
    print("Samsung scraping completed!")



def scrape_apple():
    """
    Scrape Apple iPhone models and save them to the database AS IOSs
    """
    apple_url = "https://www.gsmarena.com/apple-phones-48.php"
    print("Starting Apple scraper...")
    phone_models = fetch_phone_models(apple_url, limit=15) #LIMIT CAN BE CHANGED BUT BE CAREFUL
    for phone in phone_models:
        specs = fetch_phone_specs(phone["url"])
        if specs:
            save_phone_specs_to_db(specs)  # Pass platform='iOS'
    print("Apple scraping completed!")


def scrape_all():
    """
    Scrape both
    """
    scrape_samsung()
    scrape_apple()


if __name__ == "__main__":
    scrape_all()
