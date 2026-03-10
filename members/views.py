from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from .models import Member
from .forms import MemberForm
from accounts.permissions import StaffOrAdminMixin, AdminOrSuperAdminMixin, CooperativeAccessMixin


class MemberListView(StaffOrAdminMixin, CooperativeAccessMixin, ListView):
    """View to list all members, filtered by cooperative for non-superadmins."""
    model = Member
    template_name = 'members/member_list.html'
    context_object_name = 'members'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            qs = qs.filter(
                Q(full_name__icontains=search_query) |
                Q(citizenship_number__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(cooperative__name__icontains=search_query)
            )

        # Status filter (Blacklisted/Active)
        status_filter = self.request.GET.get('status', '').strip().lower()
        if status_filter == 'blacklisted':
            qs = qs.filter(blacklist_status=True)
        elif status_filter == 'active':
            qs = qs.filter(blacklist_status=False)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context


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
