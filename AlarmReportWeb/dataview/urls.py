from importlib.resources import path
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('chart/', views.chart),
    path('loaddata/', views.loaddata),
    path('name/', views.get_name)
]