from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from myapp import views
from myapp.views import CustomLoginView


urlpatterns = [
    path('admin/', admin.site.urls),
     # Root URL points to the login page
    path('accounts/', include('django.contrib.auth.urls')),  # Includes login, logout, and other auth views
    path('register/', views.register, name='register'),  # Registration page
    path('devices/', views.device_list, name='device_list'),

path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard page

    path('delete-device/<int:device_id>/', views.delete_device, name='delete_device'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),  # Ensures redirection
    path('device/<str:user_device_id>/', views.device_details, name='device_details'),

    path('add-device/', views.add_device, name='add_device'),

    path('device-added/<int:device_id>/', views.device_added, name='device_added'),

path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Admin dashboard URL
    path('start-scraper-all/', views.start_scraper_all, name='start_scraper_all'),
    path('start-scraper-samsung/', views.start_scraper_samsung, name='start_scraper_samsung'),
    path('start-scraper-apple/', views.start_scraper_apple, name='start_scraper_apple'),
path('', CustomLoginView.as_view(), name='login'),  # Use the custom login view
]
