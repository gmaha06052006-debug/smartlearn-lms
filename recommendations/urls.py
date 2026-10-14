from django.urls import path
from . import views

urlpatterns = [
    path('', views.recommendation_list_view, name='recommendation_list'),
    path('<int:pk>/dismiss/', views.dismiss_recommendation_view, name='dismiss_recommendation'),
]
