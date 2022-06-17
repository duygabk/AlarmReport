from importlib.resources import path
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('chart/', views.chart),
    path('load_data/', views.load_data),
    path('loaddata/', views.load_alarm_file),
    path('summary/', views.get_summary),
    path('yeildmonth/', views.load_yeild_month),
    path('chart_v2/', views.chart_v2),
    path('chart_v2/chart_detail/', views.chart_detail),
    path('chart_v2/get_ss_detail/', views.get_ss_detail),
    path('del/', views.delete_performance),
    path('download_excel/', views.download_excel),
]