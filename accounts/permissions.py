"""
Access control decorators, mixins, and helper functions for RBAC.
"""

from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy


# ==================== DECORATORS ====================

def superadmin_required(view_func):
    """Decorator to restrict view to Super Admin users only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superadmin():
            raise PermissionDenied("Only Super Admin can access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorator to restrict view to Cooperative Admin users only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin():
            raise PermissionDenied("Only Cooperative Admin can access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper


def staff_required(view_func):
    """Decorator to restrict view to Staff users only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff_user():
            raise PermissionDenied("Only Staff can access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_or_superadmin_required(view_func):
    """Decorator to restrict view to Admin or Super Admin users."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_admin() or request.user.is_superadmin()):
            raise PermissionDenied("Only Admin or Super Admin can access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper


def staff_or_admin_required(view_func):
    """Decorator to restrict view to Staff or Admin users."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_staff_user() or request.user.is_admin()):
            raise PermissionDenied("Only Staff or Admin can access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper


# Helper functions for @user_passes_test
def is_superadmin(user):
    """Check if user is Super Admin."""
    return user.is_superadmin()


def is_admin(user):
    """Check if user is Cooperative Admin."""
    return user.is_admin()


def is_staff_user(user):
    """Check if user is Staff member."""
    return user.is_staff_user()


def is_admin_or_superadmin(user):
    """Check if user is Admin or Super Admin."""
    return user.is_admin() or user.is_superadmin()


def is_staff_or_admin(user):
    """Check if user is Staff or Admin."""
    return user.is_staff_user() or user.is_admin()


# ==================== CLASS-BASED MIXINS ====================

class SuperAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to restrict class-based views to Super Admin users only."""
    
    def test_func(self):
        return self.request.user.is_superadmin()
    
    def handle_no_permission(self):
        raise PermissionDenied("Only Super Admin can access this page.")


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to restrict class-based views to Cooperative Admin users only."""
    
    def test_func(self):
        return self.request.user.is_admin()
    
    def handle_no_permission(self):
        raise PermissionDenied("Only Cooperative Admin can access this page.")


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to restrict class-based views to Staff users only."""
    
    def test_func(self):
        return self.request.user.is_staff_user()
    
    def handle_no_permission(self):
        raise PermissionDenied("Only Staff can access this page.")


class AdminOrSuperAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to restrict class-based views to Admin or Super Admin users."""
    
    def test_func(self):
        return self.request.user.is_admin() or self.request.user.is_superadmin()
    
    def handle_no_permission(self):
        raise PermissionDenied("Only Admin or Super Admin can access this page.")


class StaffOrAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to restrict class-based views to Staff or Admin users."""
    
    def test_func(self):
        return self.request.user.is_staff_user() or self.request.user.is_admin()
    
    def handle_no_permission(self):
        raise PermissionDenied("Only Staff or Admin can access this page.")


class CooperativeAccessMixin(LoginRequiredMixin):
    """
    Mixin to ensure that Admin/Staff users can only access data
    from their own cooperative.
    """
    
    def get_queryset(self):
        """Filter queryset by user's cooperative if not Super Admin."""
        queryset = super().get_queryset()
        
        if self.request.user.is_superadmin():
            return queryset
        
        # Admin and Staff can only see their cooperative's data
        if self.request.user.cooperative:
            return queryset.filter(cooperative=self.request.user.cooperative)
        
        return queryset.none()
    
    def get_context_data(self, **kwargs):
        """Add user's cooperative to context if applicable."""
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_superadmin() and self.request.user.cooperative:
            context['user_cooperative'] = self.request.user.cooperative
        return context


# ==================== UTILITY FUNCTIONS ====================

def get_user_cooperatives(user):
    """
    Get cooperatives accessible by the user.
    
    Returns:
        - Queryset of all cooperatives if user is Super Admin
        - User's single cooperative if Admin/Staff
        - Empty queryset otherwise
    """
    from cooperatives.models import Cooperative
    
    if user.is_superadmin():
        return Cooperative.objects.all()
    
    if user.cooperative:
        return Cooperative.objects.filter(id=user.cooperative.id)
    
    return Cooperative.objects.none()


def can_manage_cooperative(user, cooperative):
    """Check if user can manage a specific cooperative."""
    if user.is_superadmin():
        return True
    
    if user.is_admin() and user.cooperative == cooperative:
        return True
    
    return False


def can_view_member(user, member):
    """Check if user can view a specific member."""
    if user.is_superadmin():
        return True
    
    if user.cooperative and member.cooperative == user.cooperative:
        return True
    
    return False


def can_view_loan(user, loan):
    """Check if user can view a specific loan."""
    if user.is_superadmin():
        return True
    
    if user.cooperative and loan.cooperative == user.cooperative:
        return True
    
    return False
