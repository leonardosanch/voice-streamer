from django.urls import path
from . import views

urlpatterns = [
    # path('streams.xml', views.streams_xml, name='streams_xml'),  # <- esta línea sobra
    path('api/logs/', views.audio_logs_api, name='audio_logs_api'),
    path('logs/', views.logs_page, name='logs_page'),
]
