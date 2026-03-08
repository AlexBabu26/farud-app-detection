from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    MobileAppViewSet,
    CompareAppsAPIView,
    WatchlistViewSet,
    WatchlistToggleAPIView,
    WatchlistCheckAPIView,
    CategoryInsightsAPIView,
    DeveloperListAPIView,
    DeveloperDetailAPIView,
    CommunityReportViewSet,
)

router = DefaultRouter()
router.register(r"", MobileAppViewSet, basename="mobile-app")

urlpatterns = [
    path("compare/", CompareAppsAPIView.as_view(), name="app-compare"),
]
urlpatterns += router.urls
