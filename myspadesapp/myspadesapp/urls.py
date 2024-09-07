from django.urls import path
from spadesapp import views

urlpatterns = [
    path('upload/', views.upload_files, name='upload_files'),
    path('processing/', views.processing_view, name='processing_view'),
    path('sse/', views.sse_view, name='sse_view'),
    path('result/', views.result_page, name='result_page'),
    path('download/<path:file_name>/', views.download_file, name='download_file'),
    path('download_all/', views.download_all, name='download_all'),  
]
