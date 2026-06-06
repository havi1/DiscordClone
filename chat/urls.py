from django.urls import path
from . import views

urlpatterns = [
    path('dm/<str:username>/', views.dm_view, name='dm'),
    path('<str:room_name>/', views.room_view, name='room'),
    path('<str:room_name>/upload/', views.upload_image, name='upload_image'),
    path('<str:room_name>/upload_audio/', views.upload_audio, name='upload_audio'),
]