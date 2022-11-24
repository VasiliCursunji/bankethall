from django.contrib.auth.models import User
from django.core.serializers import serialize

from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.users.serializers import UserSerializer


class UserRegistrationView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = serializer.save(username=validated_data['email'], is_staff=True)
        user.set_password(validated_data['password'])
        user.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    serializer_class = UserSerializer
    queryset = User.objects.all()


class UserDetailView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.request.user.id)
        data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email
        }
        return Response(data=data, status=status.HTTP_200_OK)
