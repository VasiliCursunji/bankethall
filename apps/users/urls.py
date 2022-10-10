from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from apps.users.views import UserRegistrationView, UserListView

urlpatterns = [
    path('users/', UserListView.as_view(), name='get_users'),
    path('register/', UserRegistrationView.as_view(), name='token_register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]


