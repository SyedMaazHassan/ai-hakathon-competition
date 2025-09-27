from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='home'),
    path('health/', views.health_check, name='health_check'),
    path('test-email-template/', views.test_email_template, name='test_email_template'),
    path('all-request/', views.all_request, name='all_request'),
    path('appointments/', views.AppointmentsView, name='appointments'),
    path('analytics/', views.AnalyticsView, name='analytics'),
    path('emergency-calls/', views.EmergencyCallsView, name='emergency_calls'),
    path('citizen-page/', views.CitizenPageView, name='citizen_page'),
    path('  ', views.UpdateProfileView.as_view(), name='profile'),
]
