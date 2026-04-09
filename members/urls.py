from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.MemberListView.as_view(), name='member_list'),
    path('add/', views.MemberCreateView.as_view(), name='member_add'),
    path('<int:pk>/', views.MemberDetailView.as_view(), name='member_detail'),
    path('<int:pk>/edit/', views.MemberUpdateView.as_view(), name='member_edit'),
    path('<int:pk>/delete/', views.MemberDeleteView.as_view(), name='member_delete'),
    # CSV import / export
    path('export/csv/', views.MemberExportCSVView.as_view(), name='member_export_csv'),
    path('import/csv/', views.MemberImportCSVView.as_view(), name='member_import_csv'),
    path('import/csv/template/', views.MemberDownloadTemplatCSVView.as_view(), name='member_csv_template'),
]
