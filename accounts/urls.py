from django.urls import path
from . import views
#Paths relacionados al login y registro de usuarios
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]