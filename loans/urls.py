from django.urls import path
from .views import (
    LoanListView, LoanDetailView,
    LoanCreateView, LoanUpdateView,
    LoanDeleteView
)

app_name = 'loans'  # important for namespacing

urlpatterns = [
    path('', LoanListView.as_view(), name='loan_list'),
    path('create/', LoanCreateView.as_view(), name='create_loan'),
    path('<int:loan_id>/', LoanDetailView.as_view(), name='loan_detail'),
    path('<int:loan_id>/update/', LoanUpdateView.as_view(), name='update_loan'),
    path('<int:loan_id>/delete/', LoanDeleteView.as_view(), name='delete_loan'),
]