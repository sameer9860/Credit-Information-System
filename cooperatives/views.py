from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Cooperative
from accounts.forms import StaffCreationForm
from accounts.permissions import (
    SuperAdminRequiredMixin, 
    StaffOrAdminMixin, 
    CooperativeAccessMixin, 
    AdminOrSuperAdminMixin,
    superadmin_required
)


class CooperativeListView(StaffOrAdminMixin, CooperativeAccessMixin, ListView):
    """View to list cooperatives. Super Admin sees all, Admin/Staff see their own."""
    model = Cooperative
    template_name = 'cooperatives/cooperative_list.html'
    context_object_name = 'cooperatives'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            qs = qs.filter(
                Q(name__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(address__icontains=search_query) |
                Q(contact__icontains=search_query)
            )

        # Status filter
        status_filter = self.request.GET.get('status', '').strip()
        if status_filter:
            qs = qs.filter(status__iexact=status_filter)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class CooperativeCreateView(SuperAdminRequiredMixin, CreateView):
    """View for Super Admin to create a new cooperative."""
    model = Cooperative
    template_name = 'cooperatives/cooperative_form.html'
    fields = ['name', 'code', 'address', 'contact', 'status']
    success_url = reverse_lazy('cooperatives:list')

    def form_valid(self, form):
        messages.success(self.request, f"Cooperative '{form.instance.name}' created successfully.")
        return super().form_valid(form)


class CooperativeUpdateView(SuperAdminRequiredMixin, UpdateView):
    """View for Super Admin to update a cooperative."""
    model = Cooperative
    template_name = 'cooperatives/cooperative_form.html'
    fields = ['name', 'code', 'address', 'contact', 'status']
    success_url = reverse_lazy('cooperatives:list')

    def form_valid(self, form):
        messages.success(self.request, f"Cooperative '{form.instance.name}' updated successfully.")
        return super().form_valid(form)


class CooperativeDetailView(StaffOrAdminMixin, CooperativeAccessMixin, DetailView):
    """
    View for viewing cooperative details.
    Super Admin can see any, Admin/Staff can only see their own.
    """
    model = Cooperative
    template_name = 'cooperatives/cooperative_detail.html'
    context_object_name = 'cooperative'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superadmin() or self.request.user.role == 'admin':
            context['staff_form'] = StaffCreationForm(user=self.request.user, initial={'cooperative': self.object})
            # Add this line to get staff related to this cooperative
            context['cooperative_staff'] = self.object.users.all().order_by('role', 'username')
        return context


class CreateStaffView(AdminOrSuperAdminMixin, CreateView):
    """View for Admin/Super Admin to create a new staff for a cooperative."""
    form_class = StaffCreationForm
    template_name = 'cooperatives/cooperative_detail.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('cooperatives:detail', kwargs={'pk': self.request.POST.get('cooperative')})

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, f"User '{user.username}' created successfully for {user.cooperative.name}.")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        # In case of error, redirect back to the detail page with errors
        coop_id = self.request.POST.get('cooperative')
        messages.error(self.request, "Error creating staff. Please check the form.")
        # This is a bit tricky with generic views, but we can redirect back
        return redirect('cooperatives:detail', pk=coop_id)


@superadmin_required
def toggle_cooperative_status(request, pk):
    """View for Super Admin to toggle cooperative active/inactive status."""
    cooperative = get_object_or_404(Cooperative, pk=pk)
    if cooperative.status == 'active':
        cooperative.status = 'inactive'
    else:
        cooperative.status = 'active'
    cooperative.save()
    
    messages.info(request, f"Cooperative '{cooperative.name}' status set to {cooperative.status.capitalize()}.")
    return redirect('cooperatives:list')


class CooperativeDeleteView(SuperAdminRequiredMixin, DeleteView):
    """View for Super Admin to delete a cooperative."""
    model = Cooperative
    template_name = 'cooperatives/cooperative_confirm_delete.html'
    success_url = reverse_lazy('cooperatives:list')

    def delete(self, request, *args, **kwargs):
        cooperative = self.get_object()
        messages.success(request, f"Cooperative '{cooperative.name}' was deleted successfully.")
        return super().delete(request, *args, **kwargs)
