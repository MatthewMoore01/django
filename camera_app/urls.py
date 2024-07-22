from django.urls import path
from .views import capture_and_send

urlpatterns = [
    path('capture/', capture_and_send, name='capture_and_send'),
]