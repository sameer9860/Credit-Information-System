from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Loan
from .forms import LoanForm
from accounts.permissions import StaffOrAdminMixin, AdminOrSuperAdminMixin, CooperativeAccessMixin

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
        return qs

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

    def form_valid(self, form):
        # Assign cooperative from user if not superadmin
        if not self.request.user.is_superadmin():
            form.instance.cooperative = self.request.user.cooperative
        form.instance.created_by = self.request.user
        return super().form_valid(form)

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

    def form_valid(self, form):
        # Keep the original creator, don’t overwrite
        if not form.instance.created_by:
            form.instance.created_by = self.request.user
        return super().form_valid(form)
# -----------------------
# Loan Delete
# -----------------------
class LoanDeleteView(AdminOrSuperAdminMixin, CooperativeAccessMixin, LoginRequiredMixin, DeleteView):
    model = Loan
    template_name = 'loans/loan_confirm_delete.html'
    success_url = reverse_lazy('loans:loan_list')
    pk_url_kwarg = 'loan_id'