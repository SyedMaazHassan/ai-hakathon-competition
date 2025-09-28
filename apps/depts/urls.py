from django.urls import path
from . import views
from . import admin_views

app_name = "depts"


urlpatterns = [
    path("requests/", views.CitizenRequestListView.as_view(), name="citizen-requests"),
    path('calls/', views.EmergencyCallListView.as_view(), name="emergency-calls"),
    path('admin/', admin_views.admin_dashboard, name="admin-dashboard"),
]
