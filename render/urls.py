from django.urls import path

from . import views
from .views import capture_and_send

urlpatterns = [
    path('', views.index, name='index'),
    path('capture/', capture_and_send, name='capture_and_send'),
]