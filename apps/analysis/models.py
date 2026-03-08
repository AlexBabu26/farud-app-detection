from django.conf import settings
from django.db import models
from apps.apps_store.models import MobileApp


class AnalysisRun(models.Model):
    """
    Stores a single LLM classification run for an app based on its reviews.
    LLM is the only classifier; we store the raw response for auditability.
    """
    STATUS_CHOICES = [
        ("SUCCESS", "SUCCESS"),
        ("FAILED", "FAILED"),
    ]

    LABEL_CHOICES = [
        ("LEGIT", "LEGIT"),
        ("SUSPICIOUS", "SUSPICIOUS"),
        ("FRAUD", "FRAUD"),
        ("UNKNOWN", "UNKNOWN"),
    ]

    app = models.ForeignKey(MobileApp, on_delete=models.CASCADE, related_name="analysis_runs")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="analysis_runs")

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="SUCCESS")

    model_name = models.CharField(max_length=255)
    prompt_version = models.CharField(max_length=64, default="v1")

    llm_label = models.CharField(max_length=16, choices=LABEL_CHOICES, default="UNKNOWN")
    llm_confidence = models.FloatField(default=0.0)  # 0..1
    llm_rationale = models.TextField(blank=True, null=True)

    safety_score = models.IntegerField(default=0)
    sentiment_score = models.IntegerField(default=0)

    # Parsed JSON output from LLM (stringified JSON)
    llm_json = models.TextField(blank=True, null=True)

    # Full raw response (stringified)
    raw_response = models.TextField(blank=True, null=True)

    error_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["app", "created_at"]),
            models.Index(fields=["created_by", "created_at"]),
            models.Index(fields=["llm_label"]),
        ]

    def __str__(self) -> str:
        return f"AnalysisRun(app={self.app_id}, label={self.llm_label}, status={self.status})"

