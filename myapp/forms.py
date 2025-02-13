import uuid  # For generating unique device IDs
from django import forms  # Django forms module
from .models import Device, PhoneSpecs, DeviceUser  # Import necessary models

# ✅ Form for creating or updating Device Users
class DeviceUserForm(forms.ModelForm):
    class Meta:
        model = DeviceUser
        fields = ['full_name', 'position', 'location', 'phone_number', 'email']

class DeviceForm(forms.ModelForm):
    """Form for adding devices with filtered dropdowns for model and user."""

    device_user = forms.ModelChoiceField(
        queryset=DeviceUser.objects.all(),
        empty_label="Select a device user",
        required=True,
        label="Device User",
    widget = forms.Select(attrs={'id': 'id_model'})
    )

    model = forms.ModelChoiceField(
        queryset=PhoneSpecs.objects.none(),  # Set to None initially
        empty_label="Select a phone model",
        required=True,
        label="Model"
    )

    class Meta:
        model = Device
        fields = ['device_user', 'model', 'warranty_end_date']
        widgets = {
            'warranty_end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        """Dynamically filter device user queryset based on logged-in user."""
        user = kwargs.pop('user', None)  # Extract user if provided
        super().__init__(*args, **kwargs)

        if user:
            self.fields['device_user'].queryset = DeviceUser.objects.filter(app_user=user)

        # Load all phone models dynamically
        self.fields['model'].queryset = PhoneSpecs.objects.all()

    def save(self, commit=True):
        """
        Ensures the correct unique ID is set by deferring to the Device model's save method.
        """
        instance = super().save(commit=False)  # Get instance but don't save yet

        if commit:
            instance.save()  # Let `models.py` handle the unique ID assignment

        return instance  # Return the saved instance

