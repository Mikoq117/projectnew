from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404

from .models import Device

from django.contrib.auth.forms import UserCreationForm

from django.shortcuts import render, redirect

from .forms import DeviceForm  # Import the form


from myapp.models import PhoneSpecs


from django.contrib import messages
4

from .forms import DeviceForm
from .models import Device


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
    # Filter devices by the logged-in user and optimize with select_related for the model field
    devices = Device.objects.filter(app_user=request.user).select_related('model')
    return render(request, 'device_list.html', {'devices': devices})


# Add device view
@login_required




def add_device(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.app_user = request.user  # Link device to current user
            device.user_device_id = Device.generate_unique_id(request.user)   # Use your unique ID generator
            device.save()
            return redirect('device_added' , device_id=device.id)  # Redirect to a confirmation page
    else:
        form = DeviceForm()
    return render(request, 'add_device.html', {'form': form})

def generate_unique_id():
    import uuid
    return str(uuid.uuid4())
# Delete device view


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')
@login_required
def delete_device(request, device_id):
    device = get_object_or_404(Device, id=device_id, app_user=request.user)  # Ensure only the owner can delete it
    if request.method == 'POST':
        device.delete()
        return redirect('device_list')
    return redirect('device_list')
@login_required
def device_details(request, user_device_id):
    # Retrieve the specific device based on user_device_id and the logged-in user
    device = get_object_or_404(Device, user_device_id=user_device_id, app_user=request.user)
    warranty_time_left = device.warranty_time_left()
    os_support_end = device.os_support_end_date()
    os_support_time_left = device.os_support_time_left()
    return render(request, 'device_details.html', {
        'device': device,
        'warranty_time_left': warranty_time_left,
        'os_support_end': os_support_end,
        'os_support_time_left': os_support_time_left,
    })




def device_added(request, device_id):
    # Retrieve the newly added device
    device = get_object_or_404(Device, id=device_id)

    # Calculate warranty time left
    warranty_time_left = device.warranty_time_left()

    # Pass the device and warranty info to the template
    return render(request, 'device_added.html', {
        'device': device,
        'warranty_time_left': warranty_time_left
    })
