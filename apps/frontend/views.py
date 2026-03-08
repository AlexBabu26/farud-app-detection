from django.views.generic import TemplateView


class LandingView(TemplateView):
    template_name = "frontend/landing.html"


class LoginView(TemplateView):
    template_name = "frontend/login.html"


class RegisterView(TemplateView):
    template_name = "frontend/register.html"


class DashboardView(TemplateView):
    template_name = "frontend/dashboard.html"


class AppDetailView(TemplateView):
    template_name = "frontend/app_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app_id'] = kwargs.get('app_id')
        return context


class AnalysisHistoryView(TemplateView):
    template_name = "frontend/analysis_history.html"


class AnalysisDetailView(TemplateView):
    template_name = "frontend/analysis_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['run_id'] = kwargs.get('run_id')
        return context


class ProfileView(TemplateView):
    template_name = "frontend/profile.html"


class CompareView(TemplateView):
    template_name = "frontend/compare.html"


class WatchlistView(TemplateView):
    template_name = "frontend/watchlist.html"


class InsightsView(TemplateView):
    template_name = "frontend/insights.html"


class DeveloperProfileView(TemplateView):
    template_name = "frontend/developer_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['developer_name'] = kwargs.get('name', '')
        return context


class LearnView(TemplateView):
    template_name = "frontend/learn.html"


class CommunityReportsView(TemplateView):
    template_name = "frontend/community_reports.html"
