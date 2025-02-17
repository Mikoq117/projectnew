import uuid  # For generating unique device IDs
from django import forms  # Django forms module
from .models import Device, PhoneSpecs, DeviceUser  # Import necessary models

# ✅ Form for creating or updating Device Users
class DeviceUserForm(forms.ModelForm):
    class Meta:
        model = DeviceUser
        fields = ['full_name', 'position', 'location', 'phone_number', 'email']

class DeviceForm(forms.ModelForm):
    """
    Form for adding devices with a dropdown filter for models.
    """

    model = forms.ModelChoiceField(
        queryset=PhoneSpecs.objects.none(),  # Set default empty, dynamically filled in view
        empty_label="Select a phone model",
        required=True,
        label="Model",
    )

    device_user = forms.ModelChoiceField(
        queryset=DeviceUser.objects.all(),
        empty_label="Select a device user",
        required=True,
        label="Device User"
    )

    class Meta:
        model = Device
        fields = ['device_user', 'model', 'warranty_end_date']
        widgets = {
            'warranty_end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['device_user'].queryset = DeviceUser.objects.filter(app_user=user)

    def save(self, commit=True):
        """
        Ensures the correct unique ID is set by deferring to the Device model's save method.
        """
        instance = super().save(commit=False)  # Get instance but don't save yet

        if commit:
            instance.save()  # Let `models.py` handle the unique ID assignment

        return instance  # Return the saved instance

