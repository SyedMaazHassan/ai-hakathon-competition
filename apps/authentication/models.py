from django.contrib.auth.models import AbstractUser
from django.db import models
from .manager import CustomUserManager
from django_resized import ResizedImageField

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

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email