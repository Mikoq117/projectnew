from django.db import models
from django.contrib.auth.models import User




class PhoneSpecs(models.Model):
    name = models.CharField(max_length=255, unique=True)
    release_date = models.CharField(max_length=100, null=True, blank=True)
    display_size = models.CharField(max_length=50, null=True, blank=True)
    os = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class Device(models.Model):
    """Model to store devices added by users."""
    app_user = models.ForeignKey(User, on_delete=models.CASCADE)  # Links to the user who owns the device
    devicename = models.CharField(max_length=255)  # Custom device name
    owner = models.CharField(max_length=255)  # Device owner (assigned by the user)
    user_device_id = models.CharField(max_length=255, unique=True)  # Unique device ID

    def __str__(self):
        return f"{self.devicename} ({self.owner})"
