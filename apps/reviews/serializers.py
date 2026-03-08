from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = (
            "id",
            "app",
            "text",
            "rating",
            "author",
            "review_date",
            "source",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate_text(self, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Review text cannot be empty.")
        return value

    def validate_rating(self, value):
        if value is None:
            return value
        if not (1 <= value <= 5):
            raise serializers.ValidationError("rating must be between 1 and 5.")
        return value


class ReviewBulkItemSerializer(serializers.Serializer):
    text = serializers.CharField()
    rating = serializers.IntegerField(required=False, allow_null=True)
    author = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    review_date = serializers.DateTimeField(required=False, allow_null=True)
    source = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_text(self, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Review text cannot be empty.")
        return value

    def validate_rating(self, value):
        if value is None:
            return value
        if not (1 <= value <= 5):
            raise serializers.ValidationError("rating must be between 1 and 5.")
        return value


class ReviewBulkUploadSerializer(serializers.Serializer):
    app_id = serializers.IntegerField()
    reviews = ReviewBulkItemSerializer(many=True)

    def validate_reviews(self, value):
        if not value:
            raise serializers.ValidationError("reviews list cannot be empty.")
        if len(value) > 5000:
            raise serializers.ValidationError("Too many reviews in one request (max 5000).")
        return value

