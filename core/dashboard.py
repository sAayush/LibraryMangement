from django.views.generic import TemplateView


class DashboardView(TemplateView):
    """
    Simple dashboard view for the library management system
    """
    template_name = 'dashboard.html'

