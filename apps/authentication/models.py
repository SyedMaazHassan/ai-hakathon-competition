from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django_resized import ResizedImageField
from .manager import CustomUserManager
from apps.depts.models import City


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    profile_picture = ResizedImageField(
        null=True,
        blank=True,
        upload_to="Profile/profile_image",
        max_length=1000,
        force_format="WEBP",
        quality=75,
    )
    phone_regex = RegexValidator(
        regex=r'^\+92[0-9]{10}$',
        message="Phone number must be in format: '+923001234567'"
    )
    
    # Personal Information
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80, blank=True)
    phone = models.CharField(validators=[phone_regex], max_length=15, blank=True)
    # Location (for registration)
    city = models.ForeignKey(
        'depts.City',
        on_delete=models.SET_NULL,
        related_name="users",
        null=True,
        blank=True
    )
    area = models.CharField(max_length=120, blank=True)
    

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    objects = CustomUserManager()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"


