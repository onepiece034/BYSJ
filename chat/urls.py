from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('chat/history/', views.chat_history, name='chat_history'),
    path('models/', views.list_models, name='list_models'),
    path('balance/', views.get_balance, name='get_balance'),
] 