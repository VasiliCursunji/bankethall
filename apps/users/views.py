from django.contrib.auth.models import User

from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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
