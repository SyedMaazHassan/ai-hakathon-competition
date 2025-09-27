from django import forms
from django.forms.widgets import ClearableFileInput

from .models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 10, "placeholder": "Paste full job description here..."})
        }


class BulkResumeUploadForm(forms.Form):
    pass

    # Validation handled in the view to support multiple files cleanly

