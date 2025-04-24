from django.urls import path
from .views import HerbSearchView, HerbSuggestView

urlpatterns = [
    path('search/', HerbSearchView.as_view(), name='herb-search'),
    path('search/suggest/', HerbSuggestView.as_view(), name='herb-suggest'),
] 