
# WIP making form for our collect phone models that users choose from WIP
from django import forms
from .models import Device
import uuid  # For generating the unique ID


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['owner', 'devicename']
        widgets = {
            'owner': forms.TextInput(attrs={'placeholder': 'Enter device owner'}),
        }


    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.user_device_id:  # Generate the unique ID if not set
            instance.user_device_id = str(uuid.uuid4())
        if commit:
            instance.save()
        return instance
