from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings

from .models import Device
import json
from django.db.models import Count
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm

from django.shortcuts import render, redirect

from .scraper import scrape_all, scrape_samsung, scrape_apple
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
import threading
  # Import your scraper function
from datetime import date, timedelta
from .forms import DeviceForm  # Import the form
from .models import Device, PhoneSpecs, DeviceUser
from .forms import DeviceForm
from django.shortcuts import render
from django.http import HttpResponse
from .models import Device, DeviceUser
import csv
from myapp.models import PhoneSpecs
from .models import PhoneSpecs

from django.contrib import messages

from .scraper import scrape_ipads, scrape_android_tablets
from .forms import DeviceForm
from .models import Device

from django.contrib.auth.views import LoginView

#HALF OF THE IMPORTS ARENT USED, JUST LEAVING THEM THERE FOR NOW

from .forms import DeviceUserForm
from .models import DeviceUser
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q
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
def add_device(request):
    """
    View for adding a new device with filtering functionality.
    """
    # Get the selected filter from the URL query parameter
    selected_filter = request.GET.get('filter', 'all')

    # Base queryset (default: show all devices)
    queryset = PhoneSpecs.objects.all()

    # Apply filtering based on the selected filter
    if selected_filter == "iphone":
        queryset = queryset.filter(platform="iOS", device_type="Phone")
    elif selected_filter == "samsung":
        queryset = queryset.filter(platform="Android", device_type="Phone")
    elif selected_filter == "ipad":
        queryset = queryset.filter(platform="iOS", device_type="Tablet")
    elif selected_filter == "samsung-tab":
        queryset = queryset.filter(platform="Android", device_type="Tablet")

    # Initialize the form with the filtered queryset
    if request.method == "POST":
        form = DeviceForm(request.POST, user=request.user)
        form.fields['model'].queryset = queryset  # Apply filtered queryset
        if form.is_valid():
            device = form.save(commit=False)
            device.user_device_id = Device.generate_unique_id(request.user)  # Assign a unique ID
            device.app_user = request.user  # Assign the logged-in user
            device.save()
            return redirect("device_added", device_id=device.id)  # Redirect after adding
        else:
            print(form.errors)  # Debugging: Print errors if form is invalid
    else:
        form = DeviceForm(user=request.user)
        form.fields['model'].queryset = queryset  # Apply filtered queryset

    return render(request, "add_device.html", {"form": form, "selected_filter": selected_filter})




def generate_unique_id():
    import uuid
    return str(uuid.uuid4())


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


# Check if the user is an admin
def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def scrape_ipads_view(request):
    """
    View to start the iPad scraping process.
    Runs the scraper in a separate thread to prevent blocking.
    """
    try:
        thread = threading.Thread(target=scrape_ipads)
        thread.start()
        messages.success(request, "iPad scraper started successfully!")
    except Exception as e:
        messages.error(request, f"Error starting iPad scraper: {e}")

    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def scrape_android_tablets_view(request):
    """
    View to start the Android Tablet scraping process.
    Runs the scraper in a separate thread to prevent blocking.
    """
    try:
        thread = threading.Thread(target=scrape_android_tablets)
        thread.start()
        messages.success(request, "Android Tablet scraper started successfully!")
    except Exception as e:
        messages.error(request, f"Error starting Android Tablet scraper: {e}")

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





def generate_unique_id():
    import uuid
    return str(uuid.uuid4())


#dashboard

@login_required
def dashboard(request):
    devices = Device.objects.filter(app_user=request.user)

    total_devices = devices.count()
    total_device_users = devices.values("device_user").distinct().count()

    ios_count = devices.filter(model__platform="iOS").count()
    android_count = devices.filter(model__platform="Android").count()

    tablet_count = devices.filter(model__device_type="Tablet").count()
    phone_count = devices.filter(model__device_type="Phone").count()

    today = date.today()
    # Consider a warranty active if it's in the future OR if no warranty date is entered.
    active_warranty = devices.filter(Q(warranty_end_date__gte=today) | Q(warranty_end_date__isnull=True)).count()
    expired_warranty = devices.filter(warranty_end_date__lt=today).count()

    upcoming_expiry_threshold = today + timedelta(days=90)
    expiring_devices = devices.filter(
        warranty_end_date__isnull=False,
        warranty_end_date__lte=upcoming_expiry_threshold,
        warranty_end_date__gte=today
    )
    expiring_warranty_count = expiring_devices.count()

    # OS support status calculation
    os_expiring_devices = []
    os_expired_devices = []
    for device in devices:
        os_end_date = device.os_support_end()
        if os_end_date:
            if today <= os_end_date.date() <= upcoming_expiry_threshold:
                os_expiring_devices.append(device)
            elif os_end_date.date() < today:
                os_expired_devices.append(device)

    combined_os_devices = os_expiring_devices + os_expired_devices
    combined_os_count = len(combined_os_devices)
    remaining_os_support = total_devices - combined_os_count

    # Recent devices using ID ordering as a proxy for "recent"
    recent_devices = devices.order_by("-id")[:5]

    context = {
        "total_devices": total_devices,
        "total_device_users": total_device_users,
        "ios_count": ios_count,
        "android_count": android_count,
        "tablet_count": tablet_count,
        "phone_count": phone_count,
        "active_warranty": active_warranty,
        "expired_warranty": expired_warranty,
        "expiring_warranties": expiring_warranty_count,
        "expiring_devices": expiring_devices,
        "os_expiring_devices": os_expiring_devices,
        "combined_os_devices": combined_os_devices,
        "combined_os_count": combined_os_count,
        "remaining_os_support": remaining_os_support,
        "recent_devices": recent_devices,
        "devices": devices,
    }

    return render(request, "dashboard.html", context)

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


@login_required
def edit_device(request, device_id):
    """
    View for editing an existing device with filtering functionality.
    """
    device = get_object_or_404(Device, id=device_id, app_user=request.user)

    # Get filter selection from query parameter
    selected_filter = request.GET.get('filter', 'all')

    # Base queryset (default: show all devices)
    queryset = PhoneSpecs.objects.all()

    # Apply filtering based on the selected filter
    if selected_filter == "iphone":
        queryset = queryset.filter(platform="iOS", device_type="Phone")
    elif selected_filter == "samsung":
        queryset = queryset.filter(platform="Android", device_type="Phone")
    elif selected_filter == "ipad":
        queryset = queryset.filter(platform="iOS", device_type="Tablet")
    elif selected_filter == "samsung-tab":
        queryset = queryset.filter(platform="Android", device_type="Tablet")

    # Initialize the form with the filtered queryset
    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device, user=request.user)
        form.fields['model'].queryset = queryset  # Apply filtered queryset
        if form.is_valid():
            form.save()
            return redirect('device_details', user_device_id=device.user_device_id)
    else:
        form = DeviceForm(instance=device, user=request.user)
        form.fields['model'].queryset = queryset  # Apply filtered queryset

    return render(request, 'edit_device.html', {
        'form': form,
        'device': device,
        'selected_filter': selected_filter
    })



















@login_required
def device_added(request, device_id):


        device = get_object_or_404(Device, id=device_id, app_user=request.user)
        return render(request, 'device_added.html', {'device': device})


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
            device.device_user,
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




import requests
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            if not user_message:
                return JsonResponse({"error": "Empty message"}, status=400)

            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are an assistant that helps recommend new devices for a business. Recommend the top 3 and only recommend Samsung or Apple. Dot have an into to you answer but have a short conclusion.  "},


                    {"role": "user", "content": user_message}
                ]
            }

            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

            response_data = response.json()

            # Debugging: Print the entire response to see what's wrong
            print("OpenRouter Response:", response_data)

            if "choices" in response_data:
                chatbot_reply = response_data["choices"][0]["message"]["content"]
            else:
                chatbot_reply = "Sorry, I couldn't process that request."

            return JsonResponse({"reply": chatbot_reply})

        except Exception as e:
            print(f"Error in chatbot_view: {str(e)}")
            return JsonResponse({"error": "Internal server error."}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)



def help_page(request):
    return render(request, "help.html")  # Ensure the correct file path