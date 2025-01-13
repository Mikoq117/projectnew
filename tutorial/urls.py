from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth_views.LoginView.as_view(), name='login'),  # Root URL points to the login page
    path('accounts/', include('django.contrib.auth.urls')),  # Includes login, logout, and other auth views
    path('register/', views.register, name='register'),  # Registration page
    path('devices/', views.device_list, name='device_list'),

    path('delete-device/<int:device_id>/', views.delete_device, name='delete_device'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),  # Ensures redirection
    path('device/<str:user_device_id>/', views.device_details, name='device_details'),

    path('add-device/', views.add_device, name='add_device'),

    path('device-added/<int:device_id>/', views.device_added, name='device_added'),
]
