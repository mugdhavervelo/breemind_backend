from django.contrib.auth import get_user_model

User = get_user_model()


def user_get_by_email(*, email: str) -> User | None:
    """Get user by email."""
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


def user_get_by_username(*, username: str) -> User | None:
    """Get user by username."""
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None


def user_get_by_id(*, id: int) -> User | None:
    """Get user by id."""
    try:
        return User.objects.get(id=id)
    except User.DoesNotExist:
        return None
