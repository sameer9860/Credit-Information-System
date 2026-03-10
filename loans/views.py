from django.db import transaction, models
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Loan, Guarantor
from .forms import LoanForm, GuarantorForm, GuarantorFormSet, GuarantorUpdateFormSet
from accounts.permissions import StaffOrAdminMixin, AdminOrSuperAdminMixin, CooperativeAccessMixin
from members.models import Member

# -----------------------
# Loan List
# -----------------------
class LoanListView(StaffOrAdminMixin, CooperativeAccessMixin, LoginRequiredMixin, ListView):
    model = Loan
    template_name = 'loans/loan_list.html'
    context_object_name = 'loans'
    paginate_by = 10
    ordering = ['-loan_date']

    def get_queryset(self):
        qs = super().get_queryset()
        # Filter by cooperative if user is not superadmin
        if not self.request.user.is_superadmin():
            qs = qs.filter(cooperative=self.request.user.cooperative)
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            qs = qs.filter(
                Q(member__full_name__icontains=search_query) |
                Q(cooperative__name__icontains=search_query) |
                Q(guarantors__name__icontains=search_query)
            ).distinct()

        # Date filtering
        start_date = self.request.GET.get('start_date')
        if start_date:
            qs = qs.filter(loan_date__gte=start_date)
        
        due_date = self.request.GET.get('due_date')
        if due_date:
            qs = qs.filter(due_date__lte=due_date)

        # Status filter
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['due_date'] = self.request.GET.get('due_date', '')
        return context

# -----------------------
# Loan Detail
# -----------------------
class LoanDetailView(StaffOrAdminMixin, CooperativeAccessMixin, LoginRequiredMixin, DetailView):
    model = Loan
    template_name = 'loans/loan_detail.html'
    context_object_name = 'loan'
    pk_url_kwarg = 'loan_id'

# -----------------------
# Loan Create
# -----------------------
class LoanCreateView(StaffOrAdminMixin, SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Loan
    form_class = LoanForm
    template_name = 'loans/loan_form.html'
    success_url = reverse_lazy('loans:loan_list')
    success_message = "Loan for %(member)s was created successfully."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['guarantor_formset'] = GuarantorFormSet(self.request.POST)
        else:
            data['guarantor_formset'] = GuarantorFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        guarantor_formset = context['guarantor_formset']
        
        with transaction.atomic():
            # Assign cooperative from user if not superadmin
            if not self.request.user.is_superadmin():
                form.instance.cooperative = self.request.user.cooperative
            form.instance.created_by = self.request.user
            self.object = form.save() # Save the loan instance first
            
            if guarantor_formset.is_valid():
                guarantor_formset.instance = self.object # Link formset to the saved loan
                guarantor_formset.save()
            else:
                # If formset is invalid, return form_invalid for the main form
                # This will re-render the form with errors
                return self.form_invalid(form)
                
        return super().form_valid(form) # Call super().form_valid to handle redirect and success message

# -----------------------
# Loan Update
# -----------------------
class LoanUpdateView(StaffOrAdminMixin, SuccessMessageMixin, CooperativeAccessMixin, LoginRequiredMixin, UpdateView):
    model = Loan
    form_class = LoanForm
    template_name = "loans/loan_update.html"
    success_url = reverse_lazy("loans:loan_list")
    pk_url_kwarg = "loan_id"
    success_message = "Loan for %(member)s was updated successfully."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['guarantor_formset'] = GuarantorUpdateFormSet(self.request.POST, instance=self.get_object())
        else:
            data['guarantor_formset'] = GuarantorUpdateFormSet(instance=self.get_object())
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        guarantor_formset = context['guarantor_formset']
        
        with transaction.atomic():
            # Keep the original creator, don’t overwrite
            if not form.instance.created_by:
                form.instance.created_by = self.request.user
            self.object = form.save() # Save the loan instance first
            
            if guarantor_formset.is_valid():
                guarantor_formset.save()
            else:
                # If formset is invalid, return form_invalid for the main form
                # This will re-render the form with errors
                return self.form_invalid(form)
                
        return super().form_valid(form) # Call super().form_valid to handle redirect and success message
# -----------------------
# Loan Delete
# -----------------------
class LoanDeleteView(AdminOrSuperAdminMixin, CooperativeAccessMixin, LoginRequiredMixin, DeleteView):
    model = Loan
    template_name = 'loans/loan_confirm_delete.html'
    success_url = reverse_lazy('loans:loan_list')
    pk_url_kwarg = 'loan_id'

# -----------------------
# Guarantor List
# -----------------------
class GuarantorListView(StaffOrAdminMixin, LoginRequiredMixin, ListView):
    model = Guarantor
    template_name = 'loans/guarantor_list.html'
    context_object_name = 'guarantors'
    paginate_by = 10
    ordering = ['id']

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superadmin():
            qs = qs.filter(loan__cooperative=self.request.user.cooperative)
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            qs = qs.filter(
                Q(name__icontains=search_query) |
                Q(citizenship_number__icontains=search_query) |
                Q(contact_number__icontains=search_query) |
                Q(loan__member__full_name__icontains=search_query)
            )

        # Status filter
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context

# -----------------------
# Guarantor Create
# -----------------------
class GuarantorCreateView(StaffOrAdminMixin, SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Guarantor
    form_class = GuarantorForm
    template_name = 'loans/guarantor_form.html'
    success_url = reverse_lazy('loans:guarantor_list')
    success_message = "Guarantor %(name)s was added successfully."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

# -----------------------
# Guarantor Update
# -----------------------
class GuarantorUpdateView(StaffOrAdminMixin, SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Guarantor
    form_class = GuarantorForm
    template_name = 'loans/guarantor_form.html'
    success_url = reverse_lazy('loans:guarantor_list')
    success_message = "Guarantor %(name)s was updated successfully."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superadmin():
            qs = qs.filter(loan__cooperative=self.request.user.cooperative)
        return qs

# -----------------------
# Guarantor Delete
# -----------------------
class GuarantorDeleteView(AdminOrSuperAdminMixin, LoginRequiredMixin, DeleteView):
    model = Guarantor
    template_name = 'loans/guarantor_confirm_delete.html'
    success_url = reverse_lazy('loans:guarantor_list')

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superadmin():
            qs = qs.filter(loan__cooperative=self.request.user.cooperative)
        return qs

# -----------------------
# Guarantor Detail
# -----------------------
class GuarantorDetailView(StaffOrAdminMixin, LoginRequiredMixin, DetailView):
    model = Guarantor
    template_name = 'loans/guarantor_detail.html'
    context_object_name = 'guarantor'

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superadmin():
            qs = qs.filter(loan__cooperative=self.request.user.cooperative)
        return qs


# -----------------------
# Member Detail API (for auto-fill)
# -----------------------
def member_detail_api(request, member_id):
    """Returns member details as JSON for auto-filling guarantor fields."""
    try:
        member = Member.objects.get(pk=member_id)
        return JsonResponse({
            'success': True,
            'full_name': member.full_name,
            'citizenship_number': member.citizenship_number,
            'phone': member.phone,
        })
    except Member.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Member not found'}, status=404)