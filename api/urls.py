from django.urls import path
from . import views

urlpatterns = [
    path('csrf/', views.csrf, name='csrf'),
    path('all/', views.get_all, name='get_all'),
    path('upload/', views.upload_file, name='upload_file'),
    path('upload_multi/', views.upload_multi_files, name='upload_multi_file'),
    path('media/<str:file_id>/', views.get_file, name='get_file'),
    path('delete/<uuid:file_id>/', views.delete_file, name='delete_file'),
    
]

