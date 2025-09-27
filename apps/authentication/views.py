from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignupForm
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth import get_user_model
# In your views.py
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from .forms import EmailLoginForm  # Custom login form

User = get_user_model()  # Dynamically get the user model


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Do not save to database yet
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.save()  # Now save to the database
            login(request, user)

            # Redirect based on user role
            if user.is_staff or user.is_superuser:
                return redirect("home")  # Redirect admins to dashboard
            else:
                return redirect("submit_emergency_request")  # Redirect citizens to emergency request page
    else:
        form = SignupForm()
    return render(request, "authentication/signup.html", {"form": form})

class CustomLoginView(LoginView):
    template_name = "authentication/login.html"
    authentication_form = EmailLoginForm

    def get_success_url(self):
        # Check if user is admin/staff
        if self.request.user.is_staff or self.request.user.is_superuser:
            return '/'  # Redirect admins to dashboard
        else:
            return '/emergency-request/'  # Redirect citizens to emergency request page
