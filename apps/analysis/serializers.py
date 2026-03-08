from rest_framework import serializers
from .models import AnalysisRun


class AnalysisRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisRun
        fields = (
            "id",
            "app",
            "status",
            "model_name",
            "prompt_version",
            "llm_label",
            "llm_confidence",
            "llm_rationale",
            "llm_json",
            "raw_response",
            "error_message",
            "safety_score",
            "sentiment_score",
            "created_at",
        )
        read_only_fields = fields


class RunAnalysisRequestSerializer(serializers.Serializer):
    app_id = serializers.IntegerField()
    max_reviews = serializers.IntegerField(required=False, default=200, min_value=1, max_value=2000)

    def validate_max_reviews(self, value: int) -> int:
        return min(max(value, 1), 2000)


class BulkRunRequestSerializer(serializers.Serializer):
    app_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=20,
    )
    max_reviews = serializers.IntegerField(required=False, default=200, min_value=1, max_value=2000)

