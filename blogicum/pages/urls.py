from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('auth/registration/', views.register, name='registration'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
]
