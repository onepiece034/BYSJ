from django.contrib import admin
from django.urls import path, include
from .views import search_by_category

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/search/category/', search_by_category, name='search_by_category'),
    path('api/', include('api.urls')),
    path('chat/', include('chat.urls')),
    path('recognition/', include('recognition.urls')),
] 