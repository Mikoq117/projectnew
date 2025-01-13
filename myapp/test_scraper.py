import os
import django
import sys

# Add directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutorial.settings')  # Replace 'tutorial' with your project name
django.setup()

# Import models and scraper functions A
from myapp.models import PhoneSpecs
from scraper import fetch_phone_models, fetch_phone_specs, save_phone_specs_to_db

# kickstart scraping for test purposes/gathering data
def test_scraper():
    """Function to test the scraper."""
    print("Starting scraper test...")

    # Fetch phone models
    try:
        phone_models = fetch_phone_models()
        if not phone_models:
            print("No phone models fetched.")
            return
    except Exception as e:
        print(f"Error fetching phone models: {e}")
        return

    print(f"Fetched {len(phone_models)} phone models.")
    for phone in phone_models:  # Iterate over the list of dictionaries
        try:
            print(f"Phone Name: {phone['name']}, URL: {phone['url']}")
            specs = fetch_phone_specs(phone['url'])
            if specs:
                print(f"Specs for {phone['name']}: {specs}")
                save_phone_specs_to_db(specs)
            else:
                print(f"Failed to fetch specs for {phone['name']}.")
        except Exception as e:
            print(f"Error processing phone {phone['name']}: {e}")

    print("Scraper test completed!")
    print(f"Total phones in database: {PhoneSpecs.objects.count()}")


# Run the test
if __name__ == "__main__":
    test_scraper()

