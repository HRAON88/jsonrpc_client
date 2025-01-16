from django.urls import path
from .views import BaseApiView

urlpatterns = [
    path('', BaseApiView.as_view(), name='api_view'),
]