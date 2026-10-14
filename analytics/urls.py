from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_dashboard_view, name='analytics_dashboard'),
    path('chart-data/', views.api_chart_data, name='chart_data'),
]
