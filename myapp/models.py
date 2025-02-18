from django.db import models
from django.contrib.auth.models import User
from datetime import date
from datetime import datetime, timedelta
import uuid
from django.db.models import Max

class DeviceUser(models.Model):
    # Device Users are tied to the app user
    app_user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the app user
    full_name = models.CharField(max_length=255)  # Full Name
    position = models.CharField(max_length=255, null=True, blank=True)  # Optional position

    location = models.CharField(max_length=255)  # Location
    phone_number = models.CharField(max_length=15, null=True, blank=True)  # Optional phone number
    email = models.EmailField(null=True, blank=True)  # Optional email

    device_user_id = models.CharField(max_length=50, unique=True, blank=True)

    @staticmethod
    def generate_unique_device_user_id(user):
        """
        Generates a unique ID for device users based on the app user ID.
        Ensures no duplicate IDs by finding the next available number.
        Format: '<app-user ID>-U<unique number>' (e.g., 1-U1, 1-U2, 2-U1)
        """
        existing_ids = DeviceUser.objects.filter(app_user=user).values_list('device_user_id', flat=True)

        # Find the next available number
        count = 1
        while f"{user.id}-U{count}" in existing_ids:
            count += 1

        return f"{user.id}-U{count}"

    def save(self, *args, **kwargs):
        """
        Ensures `device_user_id` is assigned uniquely when saving.
        """
        if not self.device_user_id:
            self.device_user_id = self.generate_unique_device_user_id(self.app_user)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.device_user_id})"

# Define the PhoneSpecs model for saving



# Define the Device model (what users make)
from django.db import models
from django.contrib.auth.models import User




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
    )
    device_type = models.CharField(
        max_length=10,
        choices=[('Phone', 'Phone'), ('Tablet', 'Tablet')],
        default='Phone'
    )

    def __str__(self):
        return self.name





class Device(models.Model):
    app_user = models.ForeignKey(User, on_delete=models.CASCADE)  # Ensure each device belongs to a user
    device_user = models.ForeignKey("DeviceUser", on_delete=models.CASCADE)
    model = models.ForeignKey("PhoneSpecs", on_delete=models.CASCADE)
    user_device_id = models.CharField(max_length=255, unique=True)  # Unique device ID
    warranty_end_date = models.DateField(null=True, blank=True)

    @staticmethod
    def generate_unique_id(user):
        """
        Generates a unique device ID based on the user's ID and the next available number.
        This ensures no duplicate IDs are created after deletions.
        """


        # Find the highest existing device number for the user
        last_device = Device.objects.filter(app_user=user).aggregate(Max('user_device_id'))

        # Extract the last number and increment it
        last_id = last_device['user_device_id__max']

        if last_id:
            try:
                # Extract the numeric part of the last ID (e.g., "1-5" -> 5)
                last_number = int(last_id.split('-')[1])
            except (IndexError, ValueError):
                last_number = 0  # Fallback if format is incorrect
        else:
            last_number = 0  # If no devices exist yet

        # Generate the new unique ID
        return f"{user.id}-{last_number + 1}"

    def save(self, *args, **kwargs):
        """
        Override save method to ensure user_device_id is assigned automatically.
        """
        if not self.user_device_id:  # Ensure ID is only generated if missing
            self.user_device_id = Device.generate_unique_id(self.app_user)  # Assign the unique ID
        super().save(*args, **kwargs)  # Call the original save method


    def warranty_time_left(self):
        """
        Calculate the remaining warranty  for the device.

        """
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
        Calculate the support end date based on the platforms
        For iOS: Fixed 6 years from the release date
        For Android: Use the "up to X major upgrades"
        """
        try:
            # Extract the release year from the release_date field
            release_year_str = self.model.release_date.split()[0].replace(',', '')  # Remove commas as it lags
            release_year = int(release_year_str)  # Convert to an integer
            release_date = datetime(release_year, 9, 1)  # presume September release

            if self.model.platform == 'iOS':
                # Fixed 6 years of support for apple/ios devices
                support_end_date = release_date + timedelta(days=6 * 365)
                return support_end_date

            elif self.model.platform == 'Android':
                # Calculate based on the number of major Android upgrades
                if "up to" in self.model.os.lower():
                    major_upgrades = int(self.model.os.lower().split('up to ')[1].split(' ')[0])
                    support_end_date = release_date + timedelta(days=major_upgrades * 365)
                    return support_end_date

            return None  # Return none if the data is insufficient - only applies to niche cases
        except (ValueError, IndexError, AttributeError) as e:
            print(f"Error in os_support_end for {self.model.name}: {e}")
            return None

    def os_support_time_left(self):
        """
        Calculate the remaining time for OS support.

        """
        support_end_date = self.os_support_end()  # Fetch the calculated support end date
        if support_end_date:
            today = datetime.now()
            remaining = support_end_date - today
            if remaining.days > 0:
                years, days = divmod(remaining.days, 365)
                months, days = divmod(days, 30)
                return f"{years} years, {months} months, {days} days"
            else:
                return "Support has ended"
        return "No support data available"

    def realistic_usability_timeframe(self):
        """
        Calculate the realistic usability timeframe for Android devices ONLY as 75% of the support time.

        """
        try:
            support_end_date = self.os_support_end()  # Get the OS support end date
            if not support_end_date:
                return "No support data available"

            if self.model.platform == 'Android':  # Only calculate for Android devices
                today = datetime.now()
                total_days = (support_end_date - today).days
                usable_days = int(total_days * 0.75)  # 75%
                usability_date = today + timedelta(days=usable_days)
                return usability_date.strftime("%B %Y")  # make the result as "Month Year" to make it simpler

            # just give simplified veriosn of regular support end for ios
            return support_end_date.strftime("%B %Y")
        except Exception as e:
            print(f"Error calculating realistic usability timeframe for {self.model.name}: {e}")
            return "Error"

    def __str__(self):
        # Display the  model and owner when printing
        return f"{self.model.name} ({self.owner.full_name})"



