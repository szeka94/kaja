from django.conf.urls import url
from django.urls import path
from kaja.user.views import UserRegistrationView, UserLoginView, UserProfileView


app_name = "user"

urlpatterns = [
    url(r"^signup/", UserRegistrationView.as_view()),
    path("login/", UserLoginView.as_view()),
    path("profile/", UserProfileView.as_view()),
]
