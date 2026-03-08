from django.urls import path
from .views import (
    LandingView, LoginView, RegisterView, DashboardView,
    AppDetailView, AnalysisHistoryView, AnalysisDetailView, ProfileView,
    CompareView, WatchlistView, InsightsView, DeveloperProfileView,
    LearnView, CommunityReportsView,
)

urlpatterns = [
    path("", LandingView.as_view(), name="landing"),
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("apps/<int:app_id>/", AppDetailView.as_view(), name="app-detail"),
    path("analysis/", AnalysisHistoryView.as_view(), name="analysis-history"),
    path("analysis/<int:run_id>/", AnalysisDetailView.as_view(), name="analysis-detail"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("compare/", CompareView.as_view(), name="compare"),
    path("watchlist/", WatchlistView.as_view(), name="watchlist"),
    path("insights/", InsightsView.as_view(), name="insights"),
    path("developer/<str:name>/", DeveloperProfileView.as_view(), name="developer-profile"),
    path("learn/", LearnView.as_view(), name="learn"),
    path("reports/", CommunityReportsView.as_view(), name="community-reports"),
]
