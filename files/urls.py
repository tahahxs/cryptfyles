"""
Files App URL Configuration
"""
from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    path('', views.file_list, name='list'),
    path('upload/<int:group_id>/', views.upload_file, name='upload'),
    path('download/<uuid:file_id>/', views.download_file, name='download'),
    path('delete/<uuid:file_id>/', views.delete_file, name='delete'),
]
