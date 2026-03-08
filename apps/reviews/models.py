from django.db import models
from apps.apps_store.models import MobileApp


class Review(models.Model):
    """
    Stores user comments/reviews for a given mobile app.
    """
    app = models.ForeignKey(MobileApp, on_delete=models.CASCADE, related_name="reviews")

    text = models.TextField()
    rating = models.IntegerField(blank=True, null=True)  # optionally 1..5
    author = models.CharField(max_length=255, blank=True, null=True)
    review_date = models.DateTimeField(blank=True, null=True)  # original date, if known
    source = models.CharField(max_length=255, blank=True, null=True)  # e.g., Google Play

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["app", "created_at"]),
            models.Index(fields=["app", "review_date"]),
        ]

    def __str__(self) -> str:
        return f"Review({self.app_id}, {self.rating})"

