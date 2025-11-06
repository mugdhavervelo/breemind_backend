from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import signing
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from breemind_back.common.exceptions import AuthenticationError
from breemind_back.common.exceptions import NotFoundError
from breemind_back.users.selectors import user_get_by_email
from breemind_back.users.selectors import user_get_by_id
from breemind_back.users.selectors import user_get_by_username

User = get_user_model()


@transaction.atomic
def user_create(
    *,
    email: str,
    password: str,
    username: str,
    name: str | None = None,
) -> User:
    """
    Create a new user.
    """
    if user_get_by_email(email=email):
        raise AuthenticationError(
            message="User with this email already exists",
            extra={"field": "email"},
        )

    if user_get_by_username(username=username):
        raise AuthenticationError(
            message="User with this username already exists",
            extra={"field": "username"},
        )

    try:
        validate_password(password)
    except ValidationError as e:
        raise AuthenticationError(
            message="Invalid password",
            extra={"errors": e.messages},
        )

    user = User(
        email=email,
        username=username,
        name=name or "",
        is_active=False,
    )
    user.set_password(password)
    user.full_clean()
    user.save()

    return user


@transaction.atomic
def user_authenticate(
    *,
    email: str,
    password: str,
) -> User:
    """
    Authenticate a user.

    """
    user = user_get_by_email(email=email)

    if not user:
        raise AuthenticationError(
            message="Invalid credentials",
            extra={"field": "email"},
        )

    if not user.check_password(password):
        raise AuthenticationError(
            message="Invalid credentials",
            extra={"field": "password"},
        )

    if not user.is_active:
        raise AuthenticationError(
            message="Account is not active. Please verify your email.",
            extra={"field": "email"},
        )

    return user


def user_generate_email_verification_token(*, user: User) -> str:
    """
    Generate email verification token for user.

    """
    return signing.dumps({"user_id": user.id}, salt="email-verification")


def user_verify_email_token(*, token: str) -> User:
    """
    Verify email verification token.
    """
    try:
        data = signing.loads(
            token,
            salt="email-verification",
            max_age=86400,
        )  # 24 hours
        user_id = data["user_id"]
    except signing.BadSignature:
        raise AuthenticationError(
            message="Invalid or expired verification token",
            extra={"field": "token"},
        )

    user = user_get_by_id(id=user_id)
    if not user:
        raise NotFoundError(
            message="User not found",
            extra={"field": "token"},
        )

    return user


@transaction.atomic
def user_verify_email(*, user: User) -> User:
    """
    Verify user email.



    """
    user.email_verified = True
    user.email_verified_at = timezone.now()
    user.is_active = True
    user.save(update_fields=["email_verified", "email_verified_at", "is_active"])

    return user


def user_generate_password_reset_token(*, user: User) -> str:
    """
    Generate password reset token for user.

    """
    return signing.dumps({"user_id": user.id}, salt="password-reset")


def user_verify_password_reset_token(*, token: str) -> User:
    """
    Verify password reset token.


    """
    try:
        data = signing.loads(token, salt="password-reset", max_age=3600)
        user_id = data["user_id"]
    except signing.BadSignature:
        raise AuthenticationError(
            message="Invalid or expired reset token",
            extra={"field": "token"},
        )

    user = user_get_by_id(id=user_id)
    if not user:
        raise NotFoundError(
            message="User not found",
            extra={"field": "token"},
        )

    return user


@transaction.atomic
def user_reset_password(
    *,
    user: User,
    new_password: str,
) -> User:
    """
    Reset user password.

    """
    try:
        validate_password(new_password)
    except ValidationError as e:
        raise AuthenticationError(
            message="Invalid password",
            extra={"errors": e.messages},
        )

    user.set_password(new_password)
    user.save(update_fields=["password"])

    return user
