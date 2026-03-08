from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """
    Optional profile to store future metadata.
    Not strictly required, but useful for extensibility.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Profile({self.user_id})"

