

#import id and models

import uuid
from django import forms
from .models import Device, PhoneSpecs
from django import forms
from .models import DeviceUser

#define form


import uuid  # For generating unique IDs
from django import forms
from .models import Device, PhoneSpecs, DeviceUser


# Form for creating or updating Device Users
class DeviceUserForm(forms.ModelForm):
    class Meta:
        model = DeviceUser
        fields = ['full_name', 'position', 'location', 'phone_number', 'email']  # Fields to display


# Form for adding devices with dropdowns for model and owner
class DeviceForm(forms.ModelForm):
    # Dropdown for phone models
    model = forms.ModelChoiceField(
        queryset=PhoneSpecs.objects.all(),  # Fetch all PhoneSpecs objects
        empty_label="Select a phone model",  # Placeholder
        required=True,
        label="Model",
        
    )

    # Dropdown for device users
    owner = forms.ModelChoiceField(
        queryset=DeviceUser.objects.none(),
        required=True,
        label="Device User (Owner)"
    )

    class Meta:
        model = Device
        fields = ['owner', 'model', 'warranty_end_date']  # Fields to display in the form
        widgets = {
            'warranty_end_date': forms.DateInput(attrs={'type': 'date'}),  # a date picker
        }

    def __init__(self, *args, **kwargs):
        # Retrieve the logged-in user from the form initialization
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Populate the owner field
            self.fields['owner'].queryset = DeviceUser.objects.filter(app_user=user)

    def save(self, commit=True):
        # Custom save method for unique device ID
        instance = super().save(commit=False)  # Create the instance but don't save it yet
        if not instance.user_device_id:  # Check if the unique ID is not set
            instance.user_device_id = str(uuid.uuid4())  # Generate a new unique ID
        if commit:
            instance.save()  # Save the instance to the database
        return instance  # Return the saved instance

