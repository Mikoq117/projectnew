from django.db import models
from django.contrib.auth.models import User
from datetime import date
from datetime import datetime, timedelta

class PhoneSpecs(models.Model):
    unique_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    release_date = models.CharField(max_length=100, null=True, blank=True)
    display_size = models.CharField(max_length=50, null=True, blank=True)
    os = models.CharField(max_length=100, null=True, blank=True)
    platform = models.CharField(
        max_length=10,
        choices=[('iOS', 'iOS'), ('Android', 'Android')],
        default='Android'
    )  # New field to specify the platform

    class Meta:
        app_label = 'myapp'  # Explicitly associate this model with 'myapp'

    def __str__(self):
        return self.name


class Device(models.Model):
    app_user = models.ForeignKey(User, on_delete=models.CASCADE)
    owner = models.CharField(max_length=255)
    model = models.ForeignKey(PhoneSpecs, on_delete=models.CASCADE)
    user_device_id = models.CharField(max_length=255, unique=True)  # Unique device ID
    warranty_end_date = models.DateField(null=True, blank=True)

    @staticmethod
    def generate_unique_id(user):
        """
        Generate a unique ID for a device based on the user ID and their current number of devices.
        """
        device_count = Device.objects.filter(app_user=user).count()
        return f"{user.id}-{device_count + 1}"

    def warranty_time_left(self):
        if self.warranty_end_date:
            today = date.today()
            remaining = self.warranty_end_date - today
            if remaining.days > 0:
                years, days = divmod(remaining.days, 365)
                months, days = divmod(days, 30)
                return f"{years} years, {months} months, {days} days"
            else:
                return "Warranty expired"
        return "No warranty end date set"

    def os_support_end(self):
        """
        Calculate the support end date based on the platform.
        For iOS: Fixed 6 years from release date.
        For Android: Use lifespan from scraped data.
        """
        try:
            # Extract release year and clean it
            release_year_str = self.model.release_date.split()[0].replace(',', '')  # Remove commas
            release_year = int(release_year_str)  # Convert to integer
            release_date = datetime(release_year, 9, 1)  # Assuming a September release

            if self.model.platform == 'iOS':
                # Fixed 6 years of support for iPhones
                support_end_date = release_date + timedelta(days=6 * 365)
                print(f"iOS Device: {self.model.name}, Support End: {support_end_date}")
                return support_end_date

            elif self.model.platform == 'Android':
                # Extract the number of major upgrades for Android
                if "up to" in self.model.os.lower():
                    major_upgrades = int(self.model.os.lower().split('up to ')[1].split(' ')[0])
                    support_end_date = release_date + timedelta(days=major_upgrades * 365)
                    print(f"Android Device: {self.model.name}, Support End: {support_end_date}")
                    return support_end_date

            print(f"No valid support calculation for {self.model.name}")
            return None  # Default if no valid platform or data

        except (ValueError, IndexError, AttributeError) as e:
            # Handle missing or invalid data
            print(f"Error in os_support_end for {self.model.name}: {e}")
            return None

    def os_support_time_left(self):
        """
        Calculate the remaining time for OS support.
        """
        support_end_date = self.os_support_end()
        if support_end_date:
            today = datetime.now()
            remaining = support_end_date - today
            if remaining.days > 0:
                years, days = divmod(remaining.days, 365)
                months, days = divmod(days, 30)
                print(f"Device: {self.model.name}, Time Left: {years} years, {months} months, {days} days")
                return f"{years} years, {months} months, {days} days"
            else:
                print(f"Device: {self.model.name}, Support has ended")
                return "Support has ended"
        print(f"Device: {self.model.name}, No support data available")
        return "No support data available"

    def realistic_usability_timeframe(self):
        """
        Calculate the realistic usability timeframe for Android devices.
        For non-Android devices, return the regular OS support end date.
        """
        try:
            support_end_date = self.os_support_end()  # Get OS support end date
            if not support_end_date:
                return "No support data available"

            if self.model.platform == 'Android':  # Only for Android devices
                today = datetime.now()  # Current date
                total_days = (support_end_date - today).days
                usable_days = int(total_days * 0.75)  # 75% of the total time
                usability_date = today + timedelta(days=usable_days)  # Calculate the usability date
                return usability_date.strftime("%B %Y")  # Format as "Month Year"

            # For non-Android devices, return the full OS support end date
            return support_end_date.strftime("%B %Y")
        except Exception as e:
            print(f"Error calculating realistic usability timeframe for {self.model.name}: {e}")
            return "Error"
    def __str__(self):
        return f"{self.model.name} ({self.owner})"
