from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('calls.urls')),
    path('audio/', include('audio_streaming.urls')),  
]
