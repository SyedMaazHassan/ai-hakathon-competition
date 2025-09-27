from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='home'),
    path('dashboard/request-detail/', views.RequestDetailView.as_view(), name='request_detail'),
    path('health/', views.health_check, name='health_check'),
    path('emergency-request/', views.SubmitEmergencyRequestView.as_view(), name='submit_emergency_request'),
    path('emergency-request/success/', views.EmergencyRequestSuccessView.as_view(), name='emergency_request_success'),
    path('test-email-template/', views.test_email_template, name='test_email_template'),
    path('my-requests/', views.MyEmergencyRequestsView.as_view(), name='my_emergency_requests'),
    path('all-request/', views.all_request, name='all_request'),
    path('appointments/', views.AppointmentsView, name='appointments'),
    path('analytics/', views.AnalyticsView, name='analytics'),
    path('emergency-calls/', views.EmergencyCallsView, name='emergency_calls'),
    path('', views.UpdateProfileView.as_view(), name='profile'),
    path('request-complete/', views.DetailRequestView.as_view(), name='request_complete'),
]