from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignupForm
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth import get_user_model

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
            return redirect("home")
    else:
        form = SignupForm()
    return render(request, "authentication/signup.html", {"form": form})



