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

from django.shortcuts import render
from django.http import HttpResponse
from .models import Device, DeviceUser
import csv
from myapp.models import PhoneSpecs
from .models import PhoneSpecs

from django.contrib import messages


from .forms import DeviceForm
from .models import Device

from django.contrib.auth.views import LoginView

#HALF OF THE IMPORTS ARENT USED, JUST LEAVING THEM THERE FOR NOW

from .forms import DeviceUserForm
from .models import DeviceUser
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
@login_required
def device_user_list(request):
    # Fetch device users for the logged-in user
    device_users = DeviceUser.objects.filter(app_user=request.user)

    if request.method == 'POST':
        form = DeviceUserForm(request.POST)
        if form.is_valid():
            # Assign the logged-in user to the new device user
            device_user = form.save(commit=False)
            device_user.app_user = request.user
            device_user.save()
            return redirect('device_user_list')  # Redirect back to the list

    else:
        form = DeviceUserForm()

    return render(request, 'device_user_list.html', {'device_users': device_users, 'form': form})


@login_required
def delete_device_user(request, user_id):
    device_user = get_object_or_404(DeviceUser, id=user_id, app_user=request.user)
    device_user.delete() #deleting
    return redirect('device_user_list')


@login_required
def edit_device_user(request, user_id):
    device_user = get_object_or_404(DeviceUser, id=user_id, app_user=request.user)

    if request.method == 'POST':
        form = DeviceUserForm(request.POST, instance=device_user)
        if form.is_valid():
            form.save()
            return redirect('device_user_list')
    else:
        form = DeviceUserForm(instance=device_user)

    return render(request, 'edit_device_user.html', {'form': form})


class CustomLoginView(LoginView):
    """
    Custom login view to redirect admins and regular users to different dashboards.
    not using basic django one so that i can  check admin
    """
    def get_success_url(self):
        # Check for admin
        if self.request.user.is_staff:
            return '/admin-dashboard/'  # Redirect admin users to the admin dashboard
        else:
            return '/dashboard/'  # send regular users on

# User reg view
def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)   #ADMIN
def admin_dashboard(request):

    """
    Render the admin dashboard
    """
    scraped_devices = PhoneSpecs.objects.all()  # Fetch ALL saved devices
    return render(request, 'admin_dashboard.html', {
        'scraped_devices': scraped_devices,
    })

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def start_scraper_all(request):
    """
    Start the combined scraper
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
    Start  Samsung scraper.
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
    Start  Apple scraper.
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
            return redirect('device_list')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# Device list view (user-specific)!!!!!
@login_required
def device_list(request):
    # Filter devices by the logged-in user
    devices = Device.objects.filter(app_user=request.user).select_related('model')
    return render(request, 'device_list.html', {'devices': devices})


# Add device view
@login_required
def add_device(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST, user=request.user)  # Pass the logged-in user
        if form.is_valid():
            device = form.save(commit=False)
            device.app_user = request.user  # Link the device to the logged-in user
            device.user_device_id = Device.generate_unique_id(request.user)  # Generate unique ID
            device.save()
            return redirect('device_added', device_id=device.id)
    else:
        form = DeviceForm(user=request.user)  # Pass the logged-in user

    return render(request, 'add_device.html', {'form': form})


def generate_unique_id():
    import uuid
    return str(uuid.uuid4())


#dashboard
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

#delete device view
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


def edit_device(request, device_id):

        device = get_object_or_404(Device, id=device_id)

        if request.method == 'POST':
            form = DeviceForm(request.POST, instance=device)
            if form.is_valid():
                form.save()
                return redirect('device_details', user_device_id=device.user_device_id)
        else:
            form = DeviceForm(instance=device)

        return render(request, 'edit_device.html', {'form': form, 'device': device})
def device_added(request, device_id):
    # Retrieve the  added device
    device = get_object_or_404(Device, id=device_id)

    # Calculate warranty time left
    warranty_time_left = device.warranty_time_left()

    # Pass the device and warranty info to the template
    return render(request, 'device_added.html', {
        'device': device,
        'warranty_time_left': warranty_time_left
    })



def reports(request):
    devices = Device.objects.filter(app_user=request.user)
    device_users = DeviceUser.objects.filter(app_user=request.user)
    return render(request, 'reports.html', {'devices': devices, 'device_users': device_users})

def export_excel(request):
    devices = Device.objects.filter(app_user=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="device_report.csv"'

    writer = csv.writer(response)

    writer.writerow([
        'Model', 'Owner', 'Unique Device ID', 'Warranty End Date', 'Time Left (Warranty)',
        'Release Date', 'Display Size', 'Operating System', 'Platform',
        'OS Support End Date', 'Time Left for OS Support', 'Realistic Usability Timeframe'
    ])

    # Write expanded device data rows
    for device in devices:
        writer.writerow([
            device.model.name,
            device.owner,
            device.user_device_id,
            device.warranty_end_date,
            device.warranty_time_left(),
            device.model.release_date,
            device.model.display_size,
            device.model.os,
            device.model.platform,
            device.os_support_end(),
            device.os_support_time_left(),
            device.realistic_usability_timeframe()
        ])

    return response


@csrf_exempt
def export_filtered_data(request):
    if request.method == "POST":
        data = json.loads(request.body).get("data", [])

        # Create a CSV response
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="filtered_device_data.csv"'

        writer = csv.writer(response)
        # Write header row
        writer.writerow([
            "Model", "Owner", "Unique Device ID", "Warranty End Date", "Time Left (Warranty)",
            "Release Date", "Display Size", "Operating System", "Platform",
            "OS Support End Date", "Time Left for OS Support", "Realistic Usability Timeframe"
        ])

        # Write the table rows
        for row in data:
            writer.writerow(row)

        return response
