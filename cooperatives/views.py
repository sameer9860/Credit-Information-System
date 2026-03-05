from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Cooperative
from accounts.permissions import (
    SuperAdminRequiredMixin, 
    CooperativeAccessMixin,
    StaffOrAdminMixin,
    superadmin_required
)


class CooperativeListView(StaffOrAdminMixin, CooperativeAccessMixin, ListView):
    """View to list cooperatives. Super Admin sees all, Admin/Staff see their own."""
    model = Cooperative
    template_name = 'cooperatives/cooperative_list.html'
    context_object_name = 'cooperatives'


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
