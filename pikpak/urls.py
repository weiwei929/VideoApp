from django.urls import path
from . import views

app_name = 'pikpak'

urlpatterns = [
    path('', views.pikpak_home, name='home'),
    path('login/', views.pikpak_login, name='login'),
    path('files/', views.pikpak_files, name='files'),
    path('play/<int:file_id>/', views.pikpak_play, name='play'),
]
