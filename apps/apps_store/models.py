from django.conf import settings
from django.db import models


class MobileApp(models.Model):
    """
    Represents a mobile application that will be evaluated for fraud risk
    based on user reviews.
    """
    name = models.CharField(max_length=255)
    package_name = models.CharField(max_length=255, unique=True)
    store_url = models.URLField(blank=True, null=True)
    developer = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    privacy_policy_text = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mobile_apps"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_by", "created_at"]),
            models.Index(fields=["package_name"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.package_name})"


class Watchlist(models.Model):
    """User's personal watchlist of apps to monitor over time."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="watchlist_items",
    )
    app = models.ForeignKey(
        MobileApp,
        on_delete=models.CASCADE,
        related_name="watchers",
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "app")
        ordering = ["-added_at"]

    def __str__(self) -> str:
        return f"Watch({self.user_id} -> {self.app_id})"


class CommunityReport(models.Model):
    """Community-driven flag for suspicious apps."""
    REASON_CHOICES = [
        ("FRAUD", "Suspected Fraud"),
        ("PRIVACY", "Privacy Violation"),
        ("SCAM", "Financial Scam"),
        ("MALWARE", "Malware / Spyware"),
        ("MISLEADING", "Misleading Functionality"),
        ("OTHER", "Other"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="community_reports",
    )
    app = models.ForeignKey(
        MobileApp,
        on_delete=models.CASCADE,
        related_name="community_reports",
    )
    reason = models.CharField(max_length=32, choices=REASON_CHOICES)
    description = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Report({self.user_id} -> {self.app_id}: {self.reason})"

