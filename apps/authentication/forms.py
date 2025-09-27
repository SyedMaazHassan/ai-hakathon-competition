from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model

User = get_user_model()  # Dynamically get the user model


class SignupForm(UserCreationForm):
    first_name = forms.CharField(
        required=False,  # Optional field
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="First Name",
    )
    last_name = forms.CharField(
        required=True,  # Mandatory field
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Last Name",
    )

    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "password1", "password2"]

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )



class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
        label="Email",
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
        label="Password",
    )




class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("There is no user registered with this email address.")
        return email