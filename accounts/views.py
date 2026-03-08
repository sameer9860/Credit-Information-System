from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from cooperatives.models import Cooperative
from members.models import Member
from loans.models import Loan, Guarantor
from django.db.models import Count


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view for all users."""
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_superadmin():
            # System-wide stats for Super Admin
            context['total_cooperatives'] = Cooperative.objects.count()
            context['active_cooperatives'] = Cooperative.objects.filter(status='active').count()
            context['total_members'] = Member.objects.count()
            context['blacklisted_members'] = Member.objects.filter(blacklist_status=True).count()
            context['total_guarantors'] = Guarantor.objects.count()
            # Phase 10: Loan stats (Super Admin)
            context['total_loans'] = Loan.objects.count()
            context['system_overdue_loans'] = Loan.objects.filter(status='Overdue').count()
            
            context['recent_members'] = Member.objects.all().order_by('-created_at')[:5]
            context['recent_cooperatives'] = Cooperative.objects.all().order_by('-created_at')[:5]
        else:
            # Stats for Cooperative Admin/Staff
            if user.cooperative:
                coop = user.cooperative
                context['total_members'] = Member.objects.filter(cooperative=coop).count()
                context['blacklisted_members'] = Member.objects.filter(cooperative=coop, blacklist_status=True).count()
                
                # Phase 10: Loan stats (Cooperative level)
                context['active_loans'] = Loan.objects.filter(cooperative=coop, status='Active').count()
                context['overdue_loans'] = Loan.objects.filter(cooperative=coop, status='Overdue').count()
                
                context['recent_members'] = Member.objects.filter(cooperative=coop).order_by('-created_at')[:5]
                context['my_cooperative'] = coop

        return context
