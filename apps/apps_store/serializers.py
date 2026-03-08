from rest_framework import serializers
from .models import MobileApp, Watchlist, CommunityReport


class MobileAppSerializer(serializers.ModelSerializer):
    latest_analysis = serializers.SerializerMethodField()

    class Meta:
        model = MobileApp
        fields = (
            "id",
            "name",
            "package_name",
            "store_url",
            "developer",
            "category",
            "description",
            "privacy_policy_text",
            "created_at",
            "latest_analysis",
        )
        read_only_fields = ("id", "created_at", "latest_analysis")

    def get_latest_analysis(self, obj):
        run = obj.analysis_runs.filter(status="SUCCESS").order_by("-created_at").first()
        if run:
            return {
                "id": run.id,
                "label": run.llm_label,
                "safety_score": run.safety_score,
                "created_at": run.created_at,
            }
        return None

    def validate_package_name(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("package_name cannot be empty.")
        return value


class WatchlistSerializer(serializers.ModelSerializer):
    app_name = serializers.CharField(source="app.name", read_only=True)
    app_package = serializers.CharField(source="app.package_name", read_only=True)
    app_developer = serializers.CharField(source="app.developer", read_only=True)
    app_category = serializers.CharField(source="app.category", read_only=True)
    latest_analysis = serializers.SerializerMethodField()
    previous_analysis = serializers.SerializerMethodField()
    report_count = serializers.SerializerMethodField()

    class Meta:
        model = Watchlist
        fields = (
            "id", "app", "app_name", "app_package", "app_developer",
            "app_category", "added_at", "latest_analysis", "previous_analysis",
            "report_count",
        )
        read_only_fields = ("id", "added_at")

    def _get_runs(self, obj):
        return obj.app.analysis_runs.filter(status="SUCCESS").order_by("-created_at")[:2]

    def get_latest_analysis(self, obj):
        runs = list(self._get_runs(obj))
        if runs:
            r = runs[0]
            return {"id": r.id, "label": r.llm_label, "safety_score": r.safety_score, "created_at": r.created_at}
        return None

    def get_previous_analysis(self, obj):
        runs = list(self._get_runs(obj))
        if len(runs) > 1:
            r = runs[1]
            return {"id": r.id, "label": r.llm_label, "safety_score": r.safety_score, "created_at": r.created_at}
        return None

    def get_report_count(self, obj):
        return obj.app.community_reports.count()


class CommunityReportSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    app_name = serializers.CharField(source="app.name", read_only=True)

    class Meta:
        model = CommunityReport
        fields = ("id", "app", "username", "app_name", "reason", "description", "created_at")
        read_only_fields = ("id", "created_at", "username", "app_name")
