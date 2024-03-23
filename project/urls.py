from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from booking_system.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main, name="main"),
    path('trains/', trains, name="trains"),
    path('airplanes/', airplanes, name="airplanes"),
    path('register/', register_page, name="register_page"),
    path('login/', login_page, name="login_page"),
    path('register_route/', register_view, name='register'),
    path('login_route/', login_view, name='login'),
    path('subscribe/', subscribe, name="subscribe"),
    path('get_directions/', get_directions, name="get_directions"),
    path('search_ticket_plane/',search_ticket_plane,name="search_ticket_plane")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
