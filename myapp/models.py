from django.db import models
from django.contrib.auth.models import User

class Device(models.Model):
    devicename = models.CharField(max_length=255, blank=False, null=False)
    owner = models.CharField(max_length=255, blank=False, null=False)  # Represents the person assigned to the device
    app_user = models.ForeignKey(User, on_delete=models.CASCADE)  # The logged-in user who owns this record

    def __str__(self):
        return f"{self.devicename} owned by {self.owner}"
