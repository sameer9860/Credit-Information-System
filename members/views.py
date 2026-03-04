from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from .models import Member
from .forms import MemberForm
from accounts.permissions import StaffOrAdminMixin, AdminOrSuperAdminMixin, CooperativeAccessMixin


class MemberListView(StaffOrAdminMixin, CooperativeAccessMixin, ListView):
    """View to list all members, filtered by cooperative for non-superadmins."""
    model = Member
    template_name = 'members/member_list.html'
    context_object_name = 'members'
    paginate_by = 10


class MemberDetailView(StaffOrAdminMixin, CooperativeAccessMixin, DetailView):
    """View to see details of a specific member."""
    model = Member
    template_name = 'members/member_detail.html'
    context_object_name = 'member'


class MemberCreateView(StaffOrAdminMixin, SuccessMessageMixin, CreateView):
    """View to create a new member."""
    model = Member
    form_class = MemberForm
    template_name = 'members/member_form.html'
    success_url = reverse_lazy('members:member_list')
    success_message = "Member %(full_name)s was created successfully."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Assign cooperative from user if not superadmin
        if not self.request.user.is_superadmin():
            form.instance.cooperative = self.request.user.cooperative
        return super().form_valid(form)


class MemberUpdateView(StaffOrAdminMixin, SuccessMessageMixin, CooperativeAccessMixin, UpdateView):
    """View to update an existing member."""
    model = Member
    form_class = MemberForm
    template_name = 'members/member_form.html'
    success_url = reverse_lazy('members:member_list')
    success_message = "Member %(full_name)s was updated successfully."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class MemberDeleteView(AdminOrSuperAdminMixin, CooperativeAccessMixin, DeleteView):
    """View to delete a member. Only Admins can delete."""
    model = Member
    template_name = 'members/member_confirm_delete.html'
    success_url = reverse_lazy('members:member_list')
    success_message = "Member was deleted successfully."
