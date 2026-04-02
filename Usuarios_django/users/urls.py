from django.urls import path
from .views import RegisterView, LoginValidateView, ProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginValidateView.as_view(), name='login_validate'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
