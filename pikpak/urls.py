from django.urls import path
from . import views

app_name = 'pikpak'

urlpatterns = [
    path('', views.pikpak_home, name='home'),
    path('connect/', views.connect_view, name='connect'),
    path('browse/', views.browse_view, name='browse'),
    path('logout/', views.logout_view, name='logout'),
    path('player/<str:file_id>/', views.player_view, name='player'),
    path('stream/<str:file_id>/', views.stream_view, name='stream'),
    path('image/<str:file_id>/', views.image_view, name='image'),
]
