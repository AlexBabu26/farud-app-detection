from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AnalysisRunViewSet, RunAnalysisAPIView, BulkRunAnalysisAPIView,
    TrendsAPIView, ExportAnalysisAPIView,
)

router = DefaultRouter()
router.register(r"", AnalysisRunViewSet, basename="analysis-run")

urlpatterns = [
    path("run/", RunAnalysisAPIView.as_view(), name="analysis-run"),
    path("bulk-run/", BulkRunAnalysisAPIView.as_view(), name="analysis-bulk-run"),
    path("trends/<int:app_id>/", TrendsAPIView.as_view(), name="analysis-trends"),
    path("<int:run_id>/export/", ExportAnalysisAPIView.as_view(), name="analysis-export"),
]
urlpatterns += router.urls
