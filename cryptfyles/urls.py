"""
Main URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

# Change error handlers to:
handler404 = 'cryptfyles.views.custom_404'
handler500 = 'cryptfyles.views.custom_500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('groups/', include('groups.urls')),
    path('files/', include('files.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
