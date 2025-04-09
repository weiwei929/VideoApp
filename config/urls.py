from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

# 将前台的上传视频、编辑和删除URL路由注释掉，只保留管理界面的功能
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('vplayer.urls')),
    path('pikpak/', include('pikpak.urls')),
    path('favicon.ico', RedirectView.as_view(url='/static/img/favicon.png')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
