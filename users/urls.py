from django.contrib.auth.views import LogoutView
from django.urls import path

from users.apps import UsersConfig

from . import views

app_name = UsersConfig.name

urlpatterns = [
    path("register/", views.UserCreateView.as_view(), name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="mailing:home_page"), name="logout"),
    path("profile/<int:pk>", views.UserDetailView.as_view(), name="profile"),
    path("profile_update/<int:pk>", views.UserUpdateView.as_view(), name="profile_update"),
]
