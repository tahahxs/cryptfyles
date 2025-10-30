"""
Groups App URL Configuration
"""
from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    path('', views.group_list, name='list'),
    path('create/', views.group_create, name='create'),
    path('<int:pk>/', views.group_detail, name='detail'),
    path('<int:pk>/edit/', views.group_edit, name='edit'),
    path('<int:pk>/delete/', views.group_delete, name='delete'),
    path('<int:pk>/add-member/', views.add_member, name='add_member'),
    path('<int:pk>/remove-member/<int:user_id>/', views.remove_member, name='remove_member'),
]
