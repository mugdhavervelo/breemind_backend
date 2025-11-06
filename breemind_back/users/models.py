from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser, BaseModel):
    """
    Default custom user model for breemind_back.
    """

    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None
    last_name = None

    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(blank=True, null=True)

    def get_absolute_url(self) -> str:
        return reverse("users:detail", kwargs={"username": self.username})

    def mark_email_as_verified(self):
        """Mark email as verified."""
        self.email_verified = True
        self.email_verified_at = timezone.now()
        self.save(update_fields=["email_verified", "email_verified_at"])
