from importlib.resources import path
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('chart/', views.chart),
    path('loaddata/', views.load_alarm_file),
    path('summary/', views.get_summary),
    path('yeildmonth/', views.load_yeild_month),
    path('chart_v2/', views.chart_v2),
    path('del/', views.delete_performance),
]