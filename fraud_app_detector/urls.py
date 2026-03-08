from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.apps_store.views import (
    WatchlistViewSet, WatchlistToggleAPIView, WatchlistCheckAPIView,
    CategoryInsightsAPIView,
    DeveloperListAPIView, DeveloperDetailAPIView,
    CommunityReportViewSet,
)

watchlist_router = DefaultRouter()
watchlist_router.register(r"", WatchlistViewSet, basename="watchlist")

reports_router = DefaultRouter()
reports_router.register(r"", CommunityReportViewSet, basename="community-report")

urlpatterns = [
    path("admin/", admin.site.urls),

    # Frontend pages
    path("", include("apps.frontend.urls")),

    # API
    path("api/auth/", include("apps.accounts.urls")),
    path("api/apps/", include("apps.apps_store.urls")),
    path("api/reviews/", include("apps.reviews.urls")),
    path("api/analysis/", include("apps.analysis.urls")),

    # Watchlist
    path("api/watchlist/toggle/", WatchlistToggleAPIView.as_view(), name="watchlist-toggle"),
    path("api/watchlist/check/<int:app_id>/", WatchlistCheckAPIView.as_view(), name="watchlist-check"),
    path("api/watchlist/", include(watchlist_router.urls)),

    # Insights
    path("api/insights/categories/", CategoryInsightsAPIView.as_view(), name="category-insights"),
    path("api/insights/developers/", DeveloperListAPIView.as_view(), name="developer-list"),
    path("api/insights/developers/<str:name>/", DeveloperDetailAPIView.as_view(), name="developer-detail"),

    # Community Reports
    path("api/reports/", include(reports_router.urls)),
]
