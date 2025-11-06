from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework import serializers
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from breemind_back.users.selectors import user_get_by_email
from breemind_back.users.services import user_authenticate
from breemind_back.users.services import user_create
from breemind_back.users.services import user_generate_email_verification_token
from breemind_back.users.services import user_generate_password_reset_token
from breemind_back.users.services import user_reset_password
from breemind_back.users.services import user_verify_email
from breemind_back.users.services import user_verify_email_token
from breemind_back.users.services import user_verify_password_reset_token


class RegisterApi(APIView):
    """Register API."""

    permission_classes = [permissions.AllowAny]

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField(write_only=True, min_length=8)
        username = serializers.CharField(min_length=3)
        name = serializers.CharField(required=False, allow_blank=True)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        email = serializers.EmailField()
        username = serializers.CharField()
        name = serializers.CharField()

    @extend_schema(
        request=InputSerializer,
        responses={201: OutputSerializer},
    )
    def post(self, request):
        """Register a new user."""
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_create(**serializer.validated_data)

        verification_token = user_generate_email_verification_token(user=user)

        output_serializer = self.OutputSerializer(user)

        return Response(
            data={
                "user": output_serializer.data,
                "verification_token": verification_token,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginApi(APIView):
    """Login API."""

    permission_classes = [permissions.AllowAny]

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField(write_only=True)

    class OutputSerializer(serializers.Serializer):
        user = serializers.SerializerMethodField()
        token = serializers.CharField()

        def get_user(self, obj):
            return {
                "id": obj["user"].id,
                "email": obj["user"].email,
                "username": obj["user"].username,
                "name": obj["user"].name,
            }

    @extend_schema(
        request=InputSerializer,
        responses={200: OutputSerializer},
    )
    def post(self, request):
        """Authenticate a user."""
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_authenticate(**serializer.validated_data)

        token, created = Token.objects.get_or_create(user=user)

        output_data = {
            "user": user,
            "token": token.key,
        }

        output_serializer = self.OutputSerializer(output_data)

        return Response(data=output_serializer.data, status=status.HTTP_200_OK)


class VerifyEmailApi(APIView):
    """Verify email API."""

    permission_classes = [permissions.AllowAny]

    class InputSerializer(serializers.Serializer):
        token = serializers.CharField()

    class OutputSerializer(serializers.Serializer):
        message = serializers.CharField()

    @extend_schema(
        request=InputSerializer,
        responses={200: OutputSerializer},
    )
    def post(self, request):
        """Verify user email."""
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_verify_email_token(token=serializer.validated_data["token"])
        user_verify_email(user=user)

        return Response(
            data={"message": "Email verified successfully"},
            status=status.HTTP_200_OK,
        )


class ForgotPasswordApi(APIView):
    """Forgot password API."""

    permission_classes = [permissions.AllowAny]

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()

    class OutputSerializer(serializers.Serializer):
        message = serializers.CharField()

    @extend_schema(
        request=InputSerializer,
        responses={200: OutputSerializer},
    )
    def post(self, request):
        """Generate password reset token."""
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_get_by_email(email=serializer.validated_data["email"])

        if user:
            reset_token = user_generate_password_reset_token(user=user)
            return Response(
                data={
                    "message": "Password reset link sent to your email",
                    "reset_token": reset_token,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            data={"message": "If that email exists, a password reset link was sent"},
            status=status.HTTP_200_OK,
        )


class ResetPasswordApi(APIView):
    """Reset password API."""

    permission_classes = [permissions.AllowAny]

    class InputSerializer(serializers.Serializer):
        token = serializers.CharField()
        new_password = serializers.CharField(write_only=True, min_length=8)

    class OutputSerializer(serializers.Serializer):
        message = serializers.CharField()

    @extend_schema(
        request=InputSerializer,
        responses={200: OutputSerializer},
    )
    def post(self, request):
        """Reset user password."""
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_verify_password_reset_token(
            token=serializer.validated_data["token"],
        )
        user_reset_password(
            user=user,
            new_password=serializer.validated_data["new_password"],
        )

        return Response(
            data={"message": "Password reset successfully"},
            status=status.HTTP_200_OK,
        )
