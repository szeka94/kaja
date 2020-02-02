from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from kaja.user.models import UserProfile
from kaja.user.serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer


class UserRegistrationView(CreateAPIView):

    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {"message": "User registered  successfully"}
        return Response(response, status=status.HTTP_201_CREATED)


class UserLoginView(RetrieveAPIView):

    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = {"message": "User logged in  successfully", "token": serializer.data["token"]}
        return Response(response, status=status.HTTP_200_OK)


class UserProfileView(RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        qs = self.get_queryset()
        return qs.get(user=self.request.user)
