import csv
import io
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, View
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import Member
from .forms import MemberForm
from accounts.permissions import StaffOrAdminMixin, AdminOrSuperAdminMixin, CooperativeAccessMixin
from cooperatives.models import Cooperative


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


class MemberExportCSVView(StaffOrAdminMixin, View):
    """Export members to a CSV file."""

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="members_export.csv"'

        writer = csv.writer(response)
        # Header row
        writer.writerow([
            'Full Name',
            'Citizenship Number',
            'Address',
            'Phone',
            'Blacklist Status',
            'Cooperative Name',
            'Unique System ID',
            'Created At',
        ])

        # Filter by cooperative for non-superadmins
        if request.user.is_superadmin():
            members = Member.objects.select_related('cooperative').all()
        else:
            members = Member.objects.select_related('cooperative').filter(
                cooperative=request.user.cooperative
            )

        for member in members:
            writer.writerow([
                member.full_name,
                member.citizenship_number,
                member.address,
                member.phone,
                'Yes' if member.blacklist_status else 'No',
                member.cooperative.name if member.cooperative else '',
                member.unique_system_id,
                member.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        return response


class MemberImportCSVView(StaffOrAdminMixin, View):
    """Import members from a CSV file."""

    template_name = 'members/member_import_csv.html'

    def get(self, request, *args, **kwargs):
        # Provide a sample CSV download option and the upload form
        cooperatives = Cooperative.objects.all() if request.user.is_superadmin() else None
        return render(request, self.template_name, {'cooperatives': cooperatives})

    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get('csv_file')

        if not csv_file:
            messages.error(request, 'Please upload a CSV file.')
            return redirect('members:member_import_csv')

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Invalid file type. Please upload a .csv file.')
            return redirect('members:member_import_csv')

        try:
            decoded = csv_file.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(decoded))
        except Exception:
            messages.error(request, 'Could not read the file. Ensure it is a valid UTF-8 CSV.')
            return redirect('members:member_import_csv')

        created_count = 0
        skipped_count = 0
        errors = []

        for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
            full_name = row.get('Full Name', '').strip()
            citizenship_number = row.get('Citizenship Number', '').strip()
            address = row.get('Address', '').strip()
            phone = row.get('Phone', '').strip()
            blacklist_raw = row.get('Blacklist Status', 'No').strip().lower()
            cooperative_name = row.get('Cooperative Name', '').strip()

            if not full_name or not citizenship_number:
                errors.append(f"Row {row_num}: 'Full Name' and 'Citizenship Number' are required.")
                skipped_count += 1
                continue

            # Check for duplicate citizenship number
            if Member.objects.filter(citizenship_number=citizenship_number).exists():
                errors.append(f"Row {row_num}: Member with citizenship number '{citizenship_number}' already exists. Skipped.")
                skipped_count += 1
                continue

            # Determine cooperative
            if request.user.is_superadmin():
                if not cooperative_name:
                    errors.append(f"Row {row_num}: 'Cooperative Name' is required for Super Admin imports.")
                    skipped_count += 1
                    continue
                try:
                    cooperative = Cooperative.objects.get(name__iexact=cooperative_name)
                except Cooperative.DoesNotExist:
                    errors.append(f"Row {row_num}: Cooperative '{cooperative_name}' not found. Skipped.")
                    skipped_count += 1
                    continue
            else:
                cooperative = request.user.cooperative

            blacklist_status = blacklist_raw in ('yes', 'true', '1')

            try:
                Member.objects.create(
                    full_name=full_name,
                    citizenship_number=citizenship_number,
                    address=address,
                    phone=phone,
                    blacklist_status=blacklist_status,
                    cooperative=cooperative,
                )
                created_count += 1
            except Exception as e:
                errors.append(f"Row {row_num}: Error saving member - {e}")
                skipped_count += 1

        if created_count:
            messages.success(request, f'Successfully imported {created_count} member(s).')
        if skipped_count:
            messages.warning(request, f'{skipped_count} row(s) were skipped.')
        for err in errors[:10]:  # Show max 10 errors to avoid flooding the page
            messages.error(request, err)

        return redirect('members:member_list')


class MemberDownloadTemplatCSVView(StaffOrAdminMixin, View):
    """Download a blank CSV template for member import."""

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="members_import_template.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Full Name',
            'Citizenship Number',
            'Address',
            'Phone',
            'Blacklist Status',
            'Cooperative Name',
        ])
        # Write one example row
        writer.writerow([
            'Ram Bahadur',
            '12-34-56789',
            'Kathmandu, Nepal',
            '9800000000',
            'No',
            'Example Cooperative',
        ])
        return response
