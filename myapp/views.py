from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404

from .models import Device

from django.contrib.auth.forms import UserCreationForm

from django.shortcuts import render, redirect

from .scraper import scrape_all, scrape_samsung, scrape_apple
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
import threading
  # Import your scraper function

from .forms import DeviceForm  # Import the form


from myapp.models import PhoneSpecs
from .models import PhoneSpecs

from django.contrib import messages
4

from .forms import DeviceForm
from .models import Device

from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    """
    Custom login view to redirect admins and regular users to different dashboards.
    """
    def get_success_url(self):
        # Check if the logged-in user is an admin
        if self.request.user.is_staff:
            return '/admin-dashboard/'  # Redirect admin users to the admin dashboard
        else:
            return '/dashboard/'  # Redirect regular users to the user dashboard









# User registration view
def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):

    """
    Render the admin dashboard with the list of scraped devices.
    """
    scraped_devices = PhoneSpecs.objects.all()  # Fetch all saved devices
    return render(request, 'admin_dashboard.html', {
        'scraped_devices': scraped_devices,
    })

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def start_scraper_all(request):
    """
    Start the combined scraper (Samsung + Apple).
    """
    try:
        thread = threading.Thread(target=scrape_all)
        thread.start()
        messages.success(request, "The combined scraper (Samsung + Apple) has started successfully!")
    except Exception as e:
        messages.error(request, f"Error starting scraper: {e}")
    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin)
def start_scraper_samsung(request):
    """
    Start the Samsung scraper.
    """
    try:
        thread = threading.Thread(target=scrape_samsung)
        thread.start()
        messages.success(request, "The Samsung scraper has started successfully!")
    except Exception as e:
        messages.error(request, f"Error starting Samsung scraper: {e}")
    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin)
def start_scraper_apple(request):
    """
    Start the Apple scraper.
    """
    try:
        thread = threading.Thread(target=scrape_apple)
        thread.start()
        messages.success(request, "The Apple scraper has started successfully!")
    except Exception as e:
        messages.error(request, f"Error starting Apple scraper: {e}")
    return redirect('admin_dashboard')


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
    os_support_end = device.os_support_end()
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
