import json

from django.db.models import Avg, Count, Q
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analysis.models import AnalysisRun
from .models import MobileApp, Watchlist, CommunityReport
from .serializers import (
    MobileAppSerializer, WatchlistSerializer, CommunityReportSerializer,
)


class MobileAppViewSet(viewsets.ModelViewSet):
    serializer_class = MobileAppSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MobileApp.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        obj = self.get_object()
        if obj.created_by_id != self.request.user.id:
            raise PermissionDenied("You do not have permission to modify this app.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.created_by_id != self.request.user.id:
            raise PermissionDenied("You do not have permission to delete this app.")
        instance.delete()


# --- Feature 1: Comparative App Analysis ---

class CompareAppsAPIView(APIView):
    """GET /api/apps/compare/?ids=1,2,3 — Side-by-side comparison of apps."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ids_raw = request.query_params.get("ids", "")
        try:
            ids = [int(x.strip()) for x in ids_raw.split(",") if x.strip()]
        except ValueError:
            return Response({"detail": "ids must be comma-separated integers."}, status=400)

        if len(ids) < 2 or len(ids) > 5:
            return Response({"detail": "Provide 2–5 app IDs to compare."}, status=400)

        apps = MobileApp.objects.filter(id__in=ids, created_by=request.user)
        result = []
        for app in apps:
            run = app.analysis_runs.filter(status="SUCCESS").order_by("-created_at").first()
            parsed = {}
            if run and run.llm_json:
                try:
                    parsed = json.loads(run.llm_json)
                except Exception:
                    pass
            result.append({
                "id": app.id,
                "name": app.name,
                "package_name": app.package_name,
                "developer": app.developer,
                "category": app.category,
                "review_count": app.reviews.count(),
                "report_count": app.community_reports.count(),
                "analysis": {
                    "id": run.id if run else None,
                    "label": run.llm_label if run else None,
                    "safety_score": run.safety_score if run else None,
                    "confidence": run.llm_confidence if run else None,
                    "health_scores": parsed.get("health_scores", {}),
                    "recommendation_action": parsed.get("recommendation_action", ""),
                    "privacy_risk_score": parsed.get("privacy_risk_score", None),
                    "sentiment_breakdown": parsed.get("sentiment_breakdown", {}),
                } if run else None,
            })
        return Response(result)


# --- Feature 2: Watchlist ---

class WatchlistViewSet(viewsets.ModelViewSet):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).select_related("app")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user_id != self.request.user.id:
            raise PermissionDenied()
        instance.delete()


class WatchlistToggleAPIView(APIView):
    """POST /api/watchlist/toggle/ — Add or remove an app from the watchlist."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        app_id = request.data.get("app_id")
        if not app_id:
            return Response({"detail": "app_id required."}, status=400)
        try:
            app = MobileApp.objects.get(id=app_id, created_by=request.user)
        except MobileApp.DoesNotExist:
            return Response({"detail": "App not found."}, status=404)

        item, created = Watchlist.objects.get_or_create(user=request.user, app=app)
        if not created:
            item.delete()
            return Response({"watched": False})
        return Response({"watched": True}, status=201)


class WatchlistCheckAPIView(APIView):
    """GET /api/watchlist/check/<app_id>/ — Check if app is in user's watchlist."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, app_id):
        exists = Watchlist.objects.filter(user=request.user, app_id=app_id).exists()
        return Response({"watched": exists})


# --- Feature 4: Category Risk Insights ---

class CategoryInsightsAPIView(APIView):
    """GET /api/insights/categories/ — Aggregate risk stats by app category."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        categories = (
            MobileApp.objects
            .filter(created_by=request.user, category__isnull=False)
            .exclude(category="")
            .values("category")
            .annotate(
                app_count=Count("id"),
                avg_safety=Avg("analysis_runs__safety_score",
                               filter=Q(analysis_runs__status="SUCCESS")),
            )
            .order_by("-app_count")
        )

        result = []
        for cat in categories:
            fraud_count = AnalysisRun.objects.filter(
                app__created_by=request.user,
                app__category=cat["category"],
                status="SUCCESS",
                llm_label="FRAUD",
            ).values("app").distinct().count()

            suspicious_count = AnalysisRun.objects.filter(
                app__created_by=request.user,
                app__category=cat["category"],
                status="SUCCESS",
                llm_label="SUSPICIOUS",
            ).values("app").distinct().count()

            result.append({
                "category": cat["category"],
                "app_count": cat["app_count"],
                "avg_safety_score": round(cat["avg_safety"] or 0, 1),
                "fraud_app_count": fraud_count,
                "suspicious_app_count": suspicious_count,
            })
        return Response(result)


# --- Feature 5: Developer Reputation Profiles ---

class DeveloperListAPIView(APIView):
    """GET /api/insights/developers/ — List developers with aggregate stats."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        devs = (
            MobileApp.objects
            .filter(created_by=request.user, developer__isnull=False)
            .exclude(developer="")
            .values("developer")
            .annotate(
                app_count=Count("id"),
                avg_safety=Avg("analysis_runs__safety_score",
                               filter=Q(analysis_runs__status="SUCCESS")),
            )
            .order_by("-app_count")
        )
        result = []
        for d in devs:
            fraud_count = AnalysisRun.objects.filter(
                app__created_by=request.user,
                app__developer=d["developer"],
                status="SUCCESS",
                llm_label="FRAUD",
            ).values("app").distinct().count()
            result.append({
                "developer": d["developer"],
                "app_count": d["app_count"],
                "avg_safety_score": round(d["avg_safety"] or 0, 1),
                "fraud_app_count": fraud_count,
            })
        return Response(result)


class DeveloperDetailAPIView(APIView):
    """GET /api/insights/developers/<name>/ — Detailed developer profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, name):
        apps = MobileApp.objects.filter(
            created_by=request.user, developer__iexact=name
        )
        if not apps.exists():
            return Response({"detail": "Developer not found."}, status=404)

        apps_data = []
        for app in apps:
            run = app.analysis_runs.filter(status="SUCCESS").order_by("-created_at").first()
            apps_data.append({
                "id": app.id,
                "name": app.name,
                "package_name": app.package_name,
                "category": app.category,
                "review_count": app.reviews.count(),
                "latest_label": run.llm_label if run else None,
                "safety_score": run.safety_score if run else None,
            })

        agg = AnalysisRun.objects.filter(
            app__in=apps, status="SUCCESS"
        ).aggregate(avg_safety=Avg("safety_score"))

        total_reports = CommunityReport.objects.filter(app__in=apps).count()

        return Response({
            "developer": name,
            "app_count": apps.count(),
            "avg_safety_score": round(agg["avg_safety"] or 0, 1),
            "total_reports": total_reports,
            "apps": apps_data,
        })


# --- Feature 8: Community Reports ---

class CommunityReportViewSet(viewsets.ModelViewSet):
    serializer_class = CommunityReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        qs = CommunityReport.objects.all()
        app_id = self.request.query_params.get("app")
        if app_id:
            qs = qs.filter(app_id=app_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user_id != self.request.user.id:
            raise PermissionDenied("You can only delete your own reports.")
        instance.delete()
