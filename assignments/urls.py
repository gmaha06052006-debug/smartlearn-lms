from django.urls import path
from . import views

urlpatterns = [
    path('', views.assignment_list_view, name='assignment_list'),
    path('create/', views.assignment_create_view, name='assignment_create'),
    path('<int:pk>/', views.assignment_detail_view, name='assignment_detail'),
    path('submissions/<int:submission_id>/grade/', views.assignment_grade_view, name='assignment_grade'),
]
