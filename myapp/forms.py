
# WIP making form for our collect phone models that users choose from WIP


import uuid  # For generating the unique ID
from django import forms
from .models import Device, PhoneSpecs

class DeviceForm(forms.ModelForm):
    model = forms.ModelChoiceField(
        queryset=PhoneSpecs.objects.all(),
        empty_label="Select a phone model",
        required=True,
        label="Model",
    )

    class Meta:
        model = Device
        fields = ['owner', 'model', 'warranty_end_date']  # Add warranty_end_date here
        widgets = {
            'warranty_end_date': forms.DateInput(attrs={'type': 'date'}),  # Date picker in the form
        }



    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.user_device_id:  # Generate the unique ID if not set
            instance.user_device_id = str(uuid.uuid4())
        if commit:
            instance.save()
        return instance
