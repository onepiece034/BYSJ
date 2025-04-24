from django.urls import path
from . import views

urlpatterns = [
    path('api/upload', views.upload_image, name='upload_image'),
    path('api/model-info', views.get_model_info, name='get_model_info'),
    path('upload', views.upload_image, name='upload_image_mini'),
    path('model-info', views.get_model_info, name='get_model_info_mini'),
] 