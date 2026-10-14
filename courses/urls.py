from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list_view, name='home'),
    path('dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('courses/', views.course_list_view, name='course_list'),
    path('courses/<slug:slug>/', views.course_detail_view, name='course_detail'),
    path('courses/<slug:slug>/enroll/', views.enroll_course_view, name='enroll_course'),
    path('courses/<slug:course_slug>/lessons/<int:lesson_id>/', views.lesson_view, name='lesson_view'),
    path('lessons/<int:lesson_id>/toggle-progress/', views.toggle_lesson_progress_view, name='toggle_lesson_progress'),
    path('faculty/dashboard/', views.faculty_dashboard_view, name='faculty_dashboard'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
]
