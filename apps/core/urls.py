from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='home'),
    path('health/', views.health_check, name='health_check'),
    path('test-email-template/', views.test_email_template, name='test_email_template'),
    path('profile/', views.UpdateProfileView.as_view(), name='profile')
]
