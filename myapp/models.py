from django.db import models
from django.contrib.auth.models import User
from datetime import date

class PhoneSpecs(models.Model):
    unique_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    release_date = models.CharField(max_length=100, null=True, blank=True)
    display_size = models.CharField(max_length=50, null=True, blank=True)
    os = models.CharField(max_length=100, null=True, blank=True)

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

    def os_support_end_date(self):
        """
        Calculate the estimated OS support end date for the device.
        """
        if self.model.os:
            os_info = self.model.os.lower()
            if "android" in os_info and "up to" in os_info:
                try:
                    # Extract the base Android version
                    base_version = int(os_info.split("android")[1].split(",")[0].strip())
                    # Extract the number of major upgrades
                    major_upgrades = int(os_info.split("up to")[1].split("major")[0].strip())
                    # Assume Android releases a new version every year
                    current_year = date.today().year
                    release_year = current_year - (14 - base_version)  # Adjust to release year
                    support_end_year = release_year + major_upgrades

                    return date(support_end_year, 12, 31)  # Assume support ends in December
                except (ValueError, IndexError):
                    pass
        return None  # Return None if parsing failed or data is missing

    def os_support_time_left(self):
        """
        Calculate the remaining time until OS support ends.
        """
        end_date = self.os_support_end_date()
        if end_date:
            today = date.today()
            remaining = end_date - today
            if remaining.days > 0:
                years, days = divmod(remaining.days, 365)
                months, days = divmod(days, 30)
                return f"{years} years, {months} months, {days} days"
            else:
                return "OS support expired"
        return "OS support window unknown"

    def __str__(self):
        return f"{self.model.name} ({self.owner})"
