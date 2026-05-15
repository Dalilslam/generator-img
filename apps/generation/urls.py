from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.GenerationView.as_view(), name='generate'),
]