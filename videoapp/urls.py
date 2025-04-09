from django.urls import path
from . import views

app_name = 'videoapp'

urlpatterns = [
    path('', views.home, name='home'),
    path('videos/', views.video_list, name='video_list'),
    path('videos/<int:video_id>/', views.video_detail, name='video_detail'),
    path('about/', views.about, name='about'),
]
