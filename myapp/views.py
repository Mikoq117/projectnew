from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from .models import Device
from django.contrib.auth.forms import UserCreationForm

# User registration view
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after successful registration
            return redirect('device_list')  # Redirect to the device list after registration
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# Device list view (user-specific)
@login_required
def device_list(request):
    devices = Device.objects.filter(app_user=request.user)  # Filter devices by the logged-in user
    return render(request, 'device_list.html', {'devices': devices})

# Add device view
@login_required
def add_device(request):
    error_message = None
    if request.method == 'POST':
        devicename = request.POST.get('devicename')
        owner = request.POST.get('owner')

        if not devicename or not owner:
            error_message = "Both Device Name and Owner fields are required."
        else:
            # Create a device associated with the logged-in user
            Device.objects.create(devicename=devicename, owner=owner, app_user=request.user)
            return render(request, 'device_added.html', {'devicename': devicename})

    return render(request, 'add_device.html', {'error_message': error_message})

# Delete device view
@login_required
def delete_device(request, device_id):
    device = get_object_or_404(Device, id=device_id, app_user=request.user)  # Ensure only the owner can delete it
    if request.method == 'POST':
        device.delete()
        return redirect('device_list')
    return redirect('device_list')
