from django.urls import path
from . import views

urlpatterns = [
    path('csrf/', views.csrf, name='csrf'),
    path('upload/', views.upload_file, name='upload_file'),
    path('media/<str:file_id>/', views.get_file, name='get_file'),
    
]

