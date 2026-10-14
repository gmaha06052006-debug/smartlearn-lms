from django.urls import path
from . import views

urlpatterns = [
    path('', views.quiz_list_view, name='quiz_list'),
    path('<int:pk>/start/', views.quiz_start_view, name='quiz_start'),
    path('attempts/<int:attempt_id>/', views.quiz_take_view, name='quiz_take'),
    path('attempts/<int:attempt_id>/submit/', views.quiz_submit_view, name='quiz_submit'),
    path('attempts/<int:attempt_id>/result/', views.quiz_result_view, name='quiz_result'),
]
