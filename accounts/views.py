from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from cooperatives.models import Cooperative
from members.models import Member
from loans.models import Loan, Guarantor
from django.db.models import Count
from django.db.models.functions import ExtractMonth
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.views import View
from .forms import FirstTimePasswordChangeForm
import json


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

            # Chart 1: Member Status (Doughnut)
            active_members = context['total_members'] - context['blacklisted_members']
            context['member_status_labels'] = json.dumps(['Active', 'Blacklisted'])
            context['member_status_data'] = json.dumps([active_members, context['blacklisted_members']])

            # Chart 2: Loan Status (Pie)
            loan_stats = Loan.objects.values('status').annotate(count=Count('loan_id'))
            loan_labels = []
            loan_counts = []
            for stat in loan_stats:
                loan_labels.append(stat['status'])
                loan_counts.append(stat['count'])
            context['loan_status_labels'] = json.dumps(loan_labels)
            context['loan_status_data'] = json.dumps(loan_counts)

            # Chart 3: Members per Cooperative (Bar)
            coop_member_stats = Cooperative.objects.annotate(member_count=Count('members')).values('name', 'member_count')
            coop_labels = [stat['name'] for stat in coop_member_stats]
            coop_counts = [stat['member_count'] for stat in coop_member_stats]
            context['coop_member_labels'] = json.dumps(coop_labels)
            context['coop_member_data'] = json.dumps(coop_counts)

            # Chart 4: Monthly Loan Issuance (Line) - Current Year
            current_year = timezone.now().year
            monthly_loans = Loan.objects.filter(loan_date__year=current_year)\
                .annotate(month=ExtractMonth('loan_date'))\
                .values('month')\
                .annotate(count=Count('loan_id'))\
                .order_by('month')
            
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            monthly_data = [0] * 12
            for entry in monthly_loans:
                monthly_data[entry['month'] - 1] = entry['count']
            
            context['monthly_loan_labels'] = json.dumps(month_names)
            context['monthly_loan_data'] = json.dumps(monthly_data)
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


class ChangePasswordView(LoginRequiredMixin, View):
    """View to handle first-time password change."""
    def post(self, request):
        form = FirstTimePasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password1'])
            user.is_first_login = False
            user.save()
            update_session_auth_hash(request, user)  # Keep the user logged in
            messages.success(request, "Password changed successfully.")
            return redirect('accounts:dashboard')
        
        # If form is invalid, we might need to show errors. 
        # Since it's a popup, we might want to handle this via messages or redirecting back.
        for error in form.non_field_errors():
            messages.error(request, error)
        for field in form:
            for error in field.errors:
                messages.error(request, f"{field.label}: {error}")
        
        return redirect('accounts:dashboard')
