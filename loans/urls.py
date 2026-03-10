from django.urls import path
from .views import (
    LoanListView, LoanDetailView,
    LoanCreateView, LoanUpdateView,
    LoanDeleteView,
    GuarantorListView, GuarantorCreateView,
    GuarantorUpdateView, GuarantorDeleteView,
    GuarantorDetailView,
    member_detail_api
)

app_name = 'loans'  # important for namespacing

urlpatterns = [
    # Loan URLs
    path('', LoanListView.as_view(), name='loan_list'),
    path('create/', LoanCreateView.as_view(), name='create_loan'),
    path('<int:loan_id>/', LoanDetailView.as_view(), name='loan_detail'),
    path('<int:loan_id>/update/', LoanUpdateView.as_view(), name='update_loan'),
    path('<int:loan_id>/delete/', LoanDeleteView.as_view(), name='delete_loan'),

    # Guarantor URLs
    path('guarantors/', GuarantorListView.as_view(), name='guarantor_list'),
    path('guarantors/add/', GuarantorCreateView.as_view(), name='add_guarantor'),
    path('guarantors/<int:pk>/', GuarantorDetailView.as_view(), name='guarantor_detail'),
    path('guarantors/<int:pk>/update/', GuarantorUpdateView.as_view(), name='update_guarantor'),
    path('guarantors/<int:pk>/delete/', GuarantorDeleteView.as_view(), name='delete_guarantor'),

    # API
    path('api/member/<int:member_id>/', member_detail_api, name='member_detail_api'),
]