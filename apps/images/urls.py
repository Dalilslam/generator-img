from django.urls import path
from . import views

urlpatterns = [
    path('images/', views.ImageListView.as_view(), name='image-list'),
    path('images/<uuid:image_id>/favorite/', views.ImageFavoriteView.as_view(), name='image-favorite'),
]