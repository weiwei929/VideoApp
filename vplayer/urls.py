from django.urls import path
from . import views

app_name = 'vplayer'

urlpatterns = [
    path('', views.home, name='home'),
    path('videos/', views.VideoListView.as_view(), name='video_list'),
    path('videos/<int:pk>/', views.VideoDetailView.as_view(), name='video_detail'),
    path('videos/stream/<int:video_id>/', views.stream_video, name='video_stream'),  # 确保这个路径正确
    path('about/', views.about, name='about'),
]
