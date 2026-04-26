from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),

    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.create_project, name='create_project'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.edit_project, name='edit_project'),
    path('projects/<int:pk>/delete/', views.delete_project, name='delete_project'),

    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/my/', views.my_tasks, name='my_tasks'),
    path('tasks/<int:pk>/edit/', views.edit_task, name='edit_task'),
    path('tasks/<int:pk>/update-status/', views.update_task_status, name='update_task_status'),

    path('fields/', views.field_list, name='field_list'),
    path('fields/create/', views.create_field, name='create_field'),
    path('fields/<int:pk>/edit/', views.edit_field, name='edit_field'),
]