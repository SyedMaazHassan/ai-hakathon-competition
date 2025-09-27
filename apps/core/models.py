from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseModel(models.Model):
    id = models.CharField(max_length=50, primary_key=True, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    PREFIX = ""  # To be overridden by subclasses

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self.generate_custom_id()
        super().save(*args, **kwargs)

    def generate_custom_id(self):
        unique_part = uuid.uuid4()
        return f"{self.PREFIX}-{unique_part}"

    class Meta:
        abstract = True
