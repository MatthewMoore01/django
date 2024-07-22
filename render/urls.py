from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('capture/', views.capture, name='capture'),
    path('get_logs/', views.get_logs, name='get_logs'),
]