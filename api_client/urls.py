from django.urls import path
from .views import ApiView

urlpatterns = [
    path('', ApiView.as_view(), name='api_view'),
]