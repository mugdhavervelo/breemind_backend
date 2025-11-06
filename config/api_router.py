from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from breemind_back.users.api.views import UserViewSet
from breemind_back.users.auth_apis import ForgotPasswordApi
from breemind_back.users.auth_apis import LoginApi
from breemind_back.users.auth_apis import RegisterApi
from breemind_back.users.auth_apis import ResetPasswordApi
from breemind_back.users.auth_apis import VerifyEmailApi

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)

app_name = "api"
urlpatterns = [
    path("auth/register/", RegisterApi.as_view(), name="auth-register"),
    path("auth/login/", LoginApi.as_view(), name="auth-login"),
    path("auth/verify-email/", VerifyEmailApi.as_view(), name="auth-verify-email"),
    path(
        "auth/forgot-password/",
        ForgotPasswordApi.as_view(),
        name="auth-forgot-password",
    ),
    path(
        "auth/reset-password/",
        ResetPasswordApi.as_view(),
        name="auth-reset-password",
    ),
    *router.urls,
]
