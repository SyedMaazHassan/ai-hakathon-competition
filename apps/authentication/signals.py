# model
from apps.authentication.user_profile_picture_generator import generate_default_profile_picture
from django.contrib.auth import get_user_model

User = get_user_model()  # Dynamically get the user model


# assets
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile_picture_buffer = generate_default_profile_picture(
            f"{instance.first_name} {instance.last_name}"
        )
        instance.profile_picture.save(
            f"{profile_picture_buffer[0]}_profile.jpg",
            ContentFile(profile_picture_buffer[1].getvalue()),
        )
