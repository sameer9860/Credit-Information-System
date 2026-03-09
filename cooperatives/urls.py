from django.urls import path
from . import views

app_name = 'cooperatives'

urlpatterns = [
    path('', views.CooperativeListView.as_view(), name='list'),
    path('add/', views.CooperativeCreateView.as_view(), name='create'),
    path('<int:pk>/', views.CooperativeDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.CooperativeUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.CooperativeDeleteView.as_view(), name='delete'),
    path('<int:pk>/toggle-status/', views.toggle_cooperative_status, name='toggle_status'),
    path('staff/create/', views.CreateStaffView.as_view(), name='create_staff'),
]
